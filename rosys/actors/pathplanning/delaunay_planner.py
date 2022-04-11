from functools import lru_cache
from typing import Optional

import networkx as nx
import numpy as np
from scipy import ndimage, spatial

from ...helpers import angle
from ...world import Area, Obstacle, PathSegment, Point, Pose, Spline
from .delaunay_pose_group import DelaunayPoseGroup
from .fast_spline import FastSpline
from .grid import Grid
from .obstacle_map import ObstacleMap


class DelaunayPlanner:
    def __init__(self, robot_outline: list[tuple[float, float]]) -> None:
        self.robot_outline = robot_outline
        self.areas: list[Area] = []
        self.obstacles: list[Obstacle] = []
        self.obstacle_map: Optional[ObstacleMap] = None
        self.tri_points: Optional[np.array] = None
        self.tri_mesh: Optional[spatial.Delaunay] = None
        self.pose_groups: Optional[list[DelaunayPoseGroup]] = None
        self.graph: Optional[nx.DiGraph] = None

    def update_map(self, areas: list[Area], obstacles: list[Obstacle], additional_points: list[Point],
                   deadline: float) -> None:
        if self.obstacle_map and \
                self.areas == areas and \
                self.obstacles == obstacles and \
                all(self.obstacle_map.grid.contains(point, padding=1.0) for point in additional_points):
            return
        self.areas = areas
        self.obstacles = obstacles
        self._create_obstacle_map(additional_points, deadline)
        self._create_graph()

    def grow_map(self, points: list[Point], deadline: float) -> None:
        if self.obstacle_map is not None and \
                all(self.obstacle_map.grid.contains(point, padding=1.0) for point in points):
            return
        if self.obstacle_map is not None:
            bbox = self.obstacle_map.grid.bbox
            points.append(Point(x=bbox[0],         y=bbox[1]))
            points.append(Point(x=bbox[0]+bbox[2], y=bbox[1]))
            points.append(Point(x=bbox[0],         y=bbox[1]+bbox[3]))
            points.append(Point(x=bbox[0]+bbox[2], y=bbox[1]+bbox[3]))
        self._create_obstacle_map(points, deadline)
        self._create_graph()

    def _create_obstacle_map(self, additional_points: list[Point], deadline: float) -> None:
        points = [p for obstacle in self.obstacles for p in obstacle.outline]
        points += [p for area in self.areas for p in area.outline]
        points += additional_points
        grid = Grid.from_points(points, pixel_size=0.1, num_layers=36, padding=1.0)
        self.obstacle_map = ObstacleMap.from_world(self.robot_outline, self.areas, self.obstacles, grid, deadline)

    def _create_graph(self):
        min_x, min_y, size_x, size_y = self.obstacle_map.grid.bbox
        resolution = 1.0
        X, Y = np.meshgrid(np.arange(min_x, min_x + size_x - resolution / 2, resolution),
                           np.arange(min_y, min_y + size_y, resolution * np.sqrt(3) / 2))
        X[::2] += resolution / 2
        rows, cols = self.obstacle_map.grid.to_grid(X.flatten(), Y.flatten())
        keep = np.reshape([not all(self.obstacle_map.stack[int(np.round(row)), int(np.round(col)), :])
                           for row, col in zip(rows, cols)], X.shape)
        distance = ndimage.distance_transform_edt(1 - self.obstacle_map.map) * self.obstacle_map.grid.pixel_size
        D = ndimage.map_coordinates(distance, [[rows], [cols]], order=0).reshape(X.shape)
        keep[1::2, :] = np.logical_and(keep[1::2, :], D[1::2, :] < 2)
        keep[::4, 1::2] = np.logical_and(keep[::4, 1::2], D[::4, 1::2] < 2)
        keep[2::4, ::2] = np.logical_and(keep[2::4, ::2], D[2::4, ::2] < 2)
        self.tri_points = np.stack((X[keep], Y[keep]), axis=1)

        self.tri_mesh = spatial.Delaunay(self.tri_points)
        self.pose_groups = [
            DelaunayPoseGroup(
                index=i,
                point=Point(x=self.tri_points[i, 0], y=self.tri_points[i, 1]),
                neighbor_indices=_tri_neighbors(self.tri_mesh, i),
                poses=[
                    Pose(x=point[0], y=point[1], yaw=np.arctan2(neighbor[1] - point[1], neighbor[0] - point[0]))
                    for neighbor in self.tri_points[_tri_neighbors(self.tri_mesh, i)]
                ]
            )
            for i, point in enumerate(self.tri_points)
        ]

        self.graph = nx.DiGraph()
        for g, group in enumerate(self.pose_groups):
            for p in range(len(group.poses)):
                self.graph.add_node((g, p))
        for g, group in enumerate(self.pose_groups):
            for p, (pose, g_) in enumerate(zip(group.poses, group.neighbor_indices)):
                for p_, pose_ in enumerate(self.pose_groups[g_].poses):
                    if abs(angle(pose.yaw, pose_.yaw + np.pi)) < 0.01:
                        continue  # NOTE: avoid 180-degree turns
                    x, y, yaw = _generate_poses(self.obstacle_map.grid, pose, pose_)
                    if not self.obstacle_map.test(x, y, yaw).any():
                        length = np.sum(np.sqrt(np.diff(x)**2 + np.diff(y)**2))
                        self.graph.add_edge((g, p), (g_, p_), backward=False, weight=length)
                        if ((g_, p_), (g, p)) not in self.graph.edges:
                            self.graph.add_edge((g_, p_), (g, p), backward=True, weight=1.2*length)

    def search(self, start: Pose, goal: Pose) -> list[PathSegment]:
        first_segment, g, p = _find_terminal_segment(self.obstacle_map, self.pose_groups, start, True)
        last_segment, g_, p_ = _find_terminal_segment(self.obstacle_map, self.pose_groups, goal, False)

        path: list[PathSegment] = []
        path.append(first_segment)
        last_g, last_p = g, p
        try:
            for next_g, next_p in nx.shortest_path(self.graph, (g, p), (g_, p_), weight='weight')[1:]:
                last_pose = self.pose_groups[last_g].poses[last_p]
                next_pose = self.pose_groups[next_g].poses[next_p]
                backward = self.graph.edges[((last_g, last_p), (next_g, next_p))]['backward']
                spline = Spline.from_poses(last_pose, next_pose, backward=backward)
                path.append(PathSegment(spline=spline, backward=backward))
                last_g, last_p = next_g, next_p
        except nx.exception.NetworkXNoPath:
            pass
        path.append(last_segment)

        while True:
            for s in range(len(path) - 1):
                new_start = Pose(
                    x=path[s].spline.start.x,
                    y=path[s].spline.start.y,
                    yaw=path[s].spline.yaw(0) + (np.pi if path[s].backward else 0),
                )
                new_end = Pose(
                    x=path[s+1].spline.end.x,
                    y=path[s+1].spline.end.y,
                    yaw=path[s+1].spline.yaw(1) + (np.pi if path[s+1].backward else 0),
                )
                if abs(angle(new_start.yaw, new_end.yaw + np.pi)) < 0.01:
                    continue
                shortcuts = []
                for new_backward in [False, True]:
                    new_spline = Spline.from_poses(new_start, new_end, backward=new_backward)
                    if not _is_healthy(new_spline):
                        continue
                    if self.obstacle_map.test_spline(new_spline, new_backward):
                        continue
                    combined_length = _estimate_length(path[s].spline) + _estimate_length(path[s + 1].spline)
                    if .9 * _estimate_length(new_spline) > combined_length:
                        continue
                    shortcuts.append(PathSegment(spline=new_spline, backward=new_backward))
                if any(shortcuts):
                    lengths = [_estimate_length(segment.spline) for segment in shortcuts]
                    path[s] = shortcuts[np.argmin(lengths)]
                    del path[s+1]
                    break  # restart while loop
            else:
                break  # exit while loop

        return path


def _tri_neighbors(tri_mesh: spatial.Delaunay, vertex_index: int):
    return tri_mesh.vertex_neighbor_vertices[1][tri_mesh.vertex_neighbor_vertices[0][vertex_index]:
                                                tri_mesh.vertex_neighbor_vertices[0][vertex_index + 1]]


@lru_cache(maxsize=1000)
def _t_array(n: int) -> np.array:
    return np.linspace(0, 1, n)


@lru_cache(maxsize=10000)
def _generate_pose_offsets(grid: Grid, dx: float, dy: float, yaw: float, yaw_: float) -> tuple:
    spline = FastSpline(0, 0, yaw, dx, dy, yaw_, False)
    row0, col0, layer0 = grid.to_grid(0, 0, yaw)
    row1, col1, layer1 = grid.to_grid(dx, dy, yaw_)
    num_rows = int(abs(row1 - row0))
    num_cols = int(abs(col1 - col0))
    num_layers = int(abs(layer1 - layer0))
    t = _t_array(max(num_rows, num_cols, num_layers))
    return (spline.x(t), spline.y(t), spline.yaw(t) + [0, np.pi][spline.backward])


def _generate_poses(grid: Grid, pose: Pose, pose_: Pose) -> tuple:
    dx, dy, yaw = _generate_pose_offsets(grid, pose_.x - pose.x, pose_.y - pose.y, pose.yaw, pose_.yaw)
    return pose.x + dx, pose.y + dy, yaw


def _estimate_length(spline: Spline) -> float:
    dx = np.diff([spline.x(t) for t in np.linspace(0, 1, 10)])
    dy = np.diff([spline.y(t) for t in np.linspace(0, 1, 10)])
    return np.sum(np.sqrt(dx**2 + dy**2))


def _is_healthy(spline: Spline, curvature_limit: float = 10.0) -> bool:
    return np.abs(spline.max_curvature()) < curvature_limit


def _find_terminal_segment(obstacle_map: ObstacleMap, pose_groups: list[DelaunayPoseGroup],
                           terminal_pose: Pose, first: bool) -> tuple[PathSegment, int, int]:
    terminal_point = terminal_pose
    group_distances = [g.point.distance(terminal_point) for g in pose_groups]
    group_indices = np.argsort(group_distances)
    for g, group in zip(group_indices, np.array(pose_groups)[group_indices]):
        best_result = None
        best_length = np.inf
        for p, pose in enumerate(group.poses):
            for backward in [False, True]:
                poses = (terminal_pose, pose) if first else (pose, terminal_pose)
                spline = Spline.from_poses(*poses, backward=backward)
                if _is_healthy(spline) and not obstacle_map.test_spline(spline, backward):
                    length = _estimate_length(spline)
                    if length < best_length:
                        best_length = length
                        best_result = (PathSegment(spline=spline, backward=backward), g, p)
        if best_result is not None:
            return best_result
    raise RuntimeError('could not find terminal segment')

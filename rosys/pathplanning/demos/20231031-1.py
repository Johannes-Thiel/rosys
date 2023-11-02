from rosys.geometry import Point, Pose
from rosys.pathplanning.area import Area
from rosys.pathplanning.obstacle import Obstacle
from rosys.pathplanning.planner_process import PlannerSearchCommand

robot_outline = [(-0.22, -0.36), (1.07, -0.36), (1.17, 0), (1.07, 0.36), (-0.22, 0.36)]

cmd = PlannerSearchCommand(deadline=1698755173.495266, areas=[Area(outline=[Point(x=0.13897491420832986, y=33.079795245516316), Point(x=0.9368390295831577, y=29.946885978358836), Point(x=-7.371479859519884, y=28.499084724035082), Point(x=-7.601915390769407, y=28.9594717374278), Point(x=-12.605358845162307, y=28.267670000626755), Point(x=-9.730809770965502, y=30.90028003711471)], id='35608591-1861-4bf0-a747-16d90e3960bb', type='sand', color='SandyBrown', closed=True), Area(outline=[Point(x=-7.8247042543843115, y=28.819512713228576), Point(x=-7.12304987617918, y=21.491206584261445), Point(x=-13.771757736468862, y=20.768228484607167), Point(x=-14.527687646944017, y=26.10013194517687), Point(x=-12.661199289417082, y=27.873939263270174)], id='18a0a39e-8fa9-4d6e-bda1-f006a1a8e5db', type='sand', color='SandyBrown', closed=True), Area(outline=[Point(x=-14.69878593888821, y=26.054808734906644), Point(x=-19.58834958383846, y=26.108826139734887), Point(x=-19.034586911444787, y=20.111440454797556), Point(x=-17.174530856810936, y=18.949212336183383), Point(x=-18.501044172436867, y=17.33385859161733), Point(x=-18.336219211873775, y=14.539298991637086), Point(x=-19.54044022676482, y=12.137372371516422), Point(x=-16.496200319486054, y=11.943205752734873), Point(x=-13.768346610790351, y=13.435599244371893)], id='04a89121-78bf-4c65-b18c-a219868f0655', type='sand', color='SandyBrown', closed=True), Area(outline=[Point(x=-22.418307670738155, y=6.432147492077269), Point(x=-20.294341016554444, y=6.7411830770353465), Point(x=-19.97506824408273, y=12.228799920778897), Point(x=-23.48861966521211, y=15.903588658075947), Point(x=-22.316004056821697, y=11.05537480868621)], id='7544b319-4863-451d-9eec-aa2bca08d55d', type='sand', color='SandyBrown', closed=True), Area(outline=[Point(x=-21.90319747172761, y=4.896054749287612), Point(x=-20.106301354590094, y=5.828384026873663), Point(x=-16.726719714239525, y=6.004417338515281), Point(x=-16.737862625740355, y=4.365388148557717), Point(x=-19.40420825295357, y=2.224994988688279)], id='eceff456-acf3-4fa0-9729-daf3519d7358', type='sand', color='SandyBrown', closed=True), Area(outline=[Point(x=4.787948943399334, y=-1.0976359287114446), Point(x=5.255864856996492, y=0.06343287323152652), Point(x=3.2320263585600397, y=0.9126325668715558), Point(x=3.2276257344781825, y=2.393981124542152), Point(x=6.474091061442852, y=2.0008051468722394), Point(x=24.263935204849403, y=2.846670473084485), Point(x=24.07845654907991, y=7.165771058119852), Point(x=15.36042496473686, y=6.001996152749769), Point(x=6.597077637128557, y=5.948988263164841), Point(x=1.5388820304454494, y=4.546799916887675), Point(x=0.459651959673379, y=2.459952237211853), Point(x=-2.45553588847631, y=4.194181869812969), Point(x=-9.697776125676185, y=4.416042929666403), Point(x=-10.49296835419668, y=8.876451015750431), Point(x=-11.328424503423228, y=9.062929903148406), Point(x=-12.18880831913517, y=9.047332508481757), Point(x=-12.153285435375146, y=6.034308874764724), Point(x=-13.877731438863576, y=6.04901834090093), Point(x=-16.267278425842598, y=5.887167706130602), Point(x=-16.4005388427643, y=6.596130642210774), Point(x=-20.110100781873, y=6.357767799547591), Point(x=-19.705682831574904, y=11.937486055285971), Point(x=-16.595604140218633, y=11.700149650621185), Point(
    x=-13.635232892101518, y=13.284083287011828), Point(x=-14.065037944975055, y=20.351614705815944), Point(x=-6.872167521066535, y=21.398326062018185), Point(x=-7.269795423337865, y=28.286315646097634), Point(x=1.1863738692851067, y=29.804964467136486), Point(x=0.40908345041138383, y=33.195841552568865), Point(x=-9.823694566070927, y=31.107811101462726), Point(x=-14.637243145014734, y=26.245768029353528), Point(x=-19.848697538583536, y=26.219359770771696), Point(x=-18.672451545596747, y=16.975679571018045), Point(x=-19.517007583740376, y=14.455036017862591), Point(x=-23.845244428349957, y=16.177253556203212), Point(x=-22.586213476698685, y=10.875538444228956), Point(x=-22.58560083306093, y=5.345833224759808), Point(x=-19.344793088047837, y=1.81256659326522), Point(x=-16.495587621383194, y=4.275097851030251), Point(x=-13.232879930314272, y=4.031640132078634), Point(x=-11.252954976682064, y=1.4326705395630477), Point(x=-8.374224109525944, y=1.4035199540395804), Point(x=-3.205420041129351, y=2.456609257929877), Point(x=-1.6879374406886218, y=1.236457730618406), Point(x=-1.5554122960261516, y=-0.32146472979232366), Point(x=1.2723124754215864, y=-0.5807800924103195), Point(x=2.8815129017200625, y=-0.6729032273171898), Point(x=4.387694000209543, y=-1.0908445512959601)], id='40e832f0-c4c1-481f-967e-3efb3bfdc634', type=None, color='green', closed=True), Area(outline=[Point(x=6.939108652978022, y=5.781301096468923), Point(x=7.327538200536568, y=2.236522199725827), Point(x=23.956272871326966, y=3.053082324445621), Point(x=23.855867692038817, y=6.7686124472404945), Point(x=15.089916491743752, y=5.603844381563084)], id='6883fbb9-0b65-4c0b-b5cf-daf72b5eaa4f', type='sand', color='SandyBrown', closed=True)], obstacles=[Obstacle(id='e4de77d8-e001-481d-8813-7cb93efce40c', outline=[Point(x=-20.426336613882082, y=7.506586001720696), Point(x=-20.50751602890401, y=7.587765416742625), Point(x=-20.62232105861354, y=7.587765416742625), Point(x=-20.70350047363547, y=7.506586001720696), Point(x=-20.70350047363547, y=7.391780972011168), Point(x=-20.62232105861354, y=7.310601556989239), Point(x=-20.50751602890401, y=7.310601556989239), Point(x=-20.426336613882082, y=7.391780972011168)]), Obstacle(id='5b818f33-bf09-4dea-ad49-2494f1e7c7ba', outline=[Point(x=-20.07822478259053, y=7.492254264826605), Point(x=-20.15940419761246, y=7.573433679848534), Point(x=-20.27420922732199, y=7.573433679848534), Point(x=-20.355388642343918, y=7.492254264826605), Point(x=-20.355388642343918, y=7.377449235117077), Point(x=-20.27420922732199, y=7.296269820095148), Point(x=-20.15940419761246, y=7.296269820095148), Point(x=-20.07822478259053, y=7.377449235117077)]), Obstacle(id='e306fbce-14cc-4a91-ba0c-8b1328ee1084', outline=[Point(x=-19.812162270216465, y=7.484293644460433), Point(x=-19.893341685238394, y=7.565473059482362), Point(x=-20.008146714947923, y=7.565473059482362), Point(x=-20.08932612996985, y=7.484293644460433), Point(x=-20.08932612996985, y=7.369488614750905), Point(x=-20.008146714947923, y=7.2883091997289755), Point(x=-19.893341685238394, y=7.2883091997289755), Point(x=-19.812162270216465, y=7.369488614750905)])], start=Pose(x=4.112956856799466, y=-0.327868255054067, yaw=2.915927653874391, time=1698755113.4904478), goal=Pose(x=-3.532157617238227, y=31.217663011163527, yaw=1.8085542911241268, time=0))
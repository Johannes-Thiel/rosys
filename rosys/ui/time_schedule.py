from typing import Optional

from nicegui import ui

from ..actors import Automator


class Plan:

    def __init__(self) -> None:
        self.half_hours: list[bool] = [True for _ in range(24*2)]

    def is_enabled(self, hour: int, minute: Optional[int] = None) -> bool:
        index = hour * 2
        first_half, second_half = self.half_hours[index:index+2]
        if minute is None:
            return first_half and second_half
        if minute < 0 or minute > 59:
            raise ValueError(f'minutes must be between 0 and 59, not {minute}')
        if minute < 30 and first_half:
            return True
        if minute >= 30 and second_half:
            return True
        return False

    def toggle(self, hour: int, minute: Optional[int] = None) -> bool:
        index = hour * 2
        if minute is None:
            self.half_hours[index] = self.half_hours[index+1] = not self.is_enabled(hour)
            return
        if minute < 0 or minute > 59:
            raise ValueError(f'minutes must be between 0 and 59, not {minute}')
        if minute < 30:
            self.half_hours[index] = not self.is_enabled(hour, minute)
        if minute >= 30:
            self.half_hours[index] = not self.is_enabled(hour, minute)


class TimeSchedule:

    def __init__(self,
                 automator: Automator,
                 ) -> None:
        self.automator = automator
        self.plan = Plan()
        self.buttons: list[tuple(ui.button, ui.button, ui.button)] = []

        with ui.row().style(replace='gap: 0.3em'):
            for i in range(24):
                with ui.column().style(replace='gap: 0.3em'):
                    hour = ui.button(str(i).zfill(2), on_click=lambda _, i=i: self.toggle(i)).props('unelevated dense')
                    w = 0.8
                    with ui.row().style(replace='gap: 0.1em'):
                        first_half = ui.button('', on_click=lambda _, i=i: self.toggle(i, 0)). \
                            props('unelevated dense').style(f'width:{w}em')
                        second_half = ui.button('', on_click=lambda _, i=i: self.toggle(i, 30)). \
                            props('unelevated dense').style(f'width:{w}em')
                self.buttons.append((hour, first_half, second_half))
        self.update()

    def update(self):
        for i, hour_buttons in enumerate(self.buttons):
            hour_buttons[0].classes(replace='bg-positive' if self.plan.is_enabled(i) else 'bg-negative')
            hour_buttons[1].classes(replace='bg-positive' if self.plan.is_enabled(i, 0) else 'bg-negative')
            hour_buttons[2].classes(replace='bg-positive' if self.plan.is_enabled(i, 30) else 'bg-negative')

    def toggle(self, hour: int, minute: Optional[int] = None):
        self.plan.toggle(hour, minute)
        self.update()

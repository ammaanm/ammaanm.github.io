import datetime
import inspect
import re
from asyncio import ensure_future, run
from itertools import islice
from typing import Any, Callable, Coroutine, Literal, Self


import flet as ft
import flet_contrib.color_picker
from webcolors import name_to_hex

name2hex: Callable[[str], str] = lambda a: a if (a or "cyan").startswith("#") and (len(a)-1) in (3, 6) else name_to_hex(a)

class SetterProperty(object):
    def __init__(self, func, doc=None):
        self.func = func
        self.__doc__ = doc if doc is not None else func.__doc__
    def __set__(self, obj, value):
        return self.func(obj, value)
def batched(iterable, n):
    "Batch data into lists of length n. The last batch may be shorter."
    # batched('ABCDEFG', 3) --> ABC DEF G
    it = iter(iterable)
    while True:
        batch = list(islice(it, n))
        if not batch:
            return
        yield batch
# from random import randint

    

#{NS}.chart.{statname} = {timestamp}
#{NS}.chartdata.{chartname}.{timestamp} = {value}
#{NS}.chartstats.{statname}.min = {value}
#{NS}.chartstats.{statname}.max = {value}
#{NS}.chartstats.{statname}.color = {value}


# BOTTOM_PAGE = "/AddValues"
# DATE_FORMAT ="%b %a %d, %I:%M %p %Y"
DATE_FORMAT ="%b %a %d, %H:%M"
NS = "andrey_ma.stat_tracker"

async def getChartValues(page:ft.Page, chart:str):
    for key in sorted(await page.client_storage.get_keys_async(f"{NS}.chartdata.{chart}")):
        yield (
            key.split(".")[-1],
            await page.client_storage.get_async(key)
            )
async def getSortedCharts(page: ft.Page, default_sort:Literal["time","a-z"] = "a-z"):
    class SortedValues():
        @property
        def values(self) -> tuple[str, ...]:
            return tuple(self._charts_sorted)
        @property
        def sort(self) -> tuple[str, bool]:
            return self.__sort
        
        @sort.setter
        def sort(self, new_sort:tuple[Literal["time","a-z"], bool]) -> None:
            match new_sort[0]:
                case "time":
                    self._charts_sorted.sort(key=lambda a: self.__charts_unsorted[a], reverse=new_sort[1])
                case "a-z":
                    self._charts_sorted.sort(reverse=new_sort[1])
                case a:
                    raise TypeError(f"can not find sortion '{a}'")
            self.__sort = new_sort
        def __init__(self, charts:dict[str, int], sort:Literal["time","a-z"] = "a-z") -> None:
            self.__charts_unsorted = charts
            self._charts_sorted = list(charts.keys())
            self.sort = sort, False
            
    class Control():
        def __init__(self, values:SortedValues):
            self.row = ft.Row(controls = [
                ft.Chip(ft.Text("A-Z+"),on_click=self.sort),
                ft.Chip(ft.Text("Time"), on_click=self.sort), 
            ])
            self.__values = values
            self.__on_sort = None
        async def sort(self, e):
            sort = e.control.label.value or ""
            if sort.rstrip("+-").lower() == self.__values.sort[0]:
                self.__values.sort = (self.__values.sort[0] or "").lower(), not self.__values.sort[1] #type:ignore
            else:
                self.__values.sort = sort.rstrip("+-").lower(), False
            for cont in self.row.controls:
                cont.label.value = cont.label.value.rstrip("-+") #type:ignore
            e.control.label.value = self.__values.sort[0].title() + ("-" if self.__values.sort[1] else "+")
            if inspect.iscoroutinefunction(self.__on_sort):
                await self.__on_sort(self)
            elif self.__on_sort:
                self.__on_sort(self) #type:ignore
            e.control.page.update()
        @property
        def chart_names(self):
            return self.__values.values
        @SetterProperty
        def on_sort(self, value:Callable[[Self], None]|Coroutine):
            self.__on_sort = value
    
    # charts = SortedValues({
    #     a:
    # })

    charts = SortedValues({i.split(".")[-1]:await page.client_storage.get_async(i) 
                  for i in await page.client_storage.get_keys_async(f"{NS}.chart.")}, default_sort)
    
    return Control(charts)

def ColorPicker(color="#c8df6f", width=300):
    def open_color_picker(e):
        e.control.page.open(d) #type:ignore
        e.control.page.update()
    
    color_picker = flet_contrib.color_picker.ColorPicker(color,width)
    color_icon = ft.IconButton(icon=ft.icons.BRUSH, icon_color=color, 
                               on_click=open_color_picker, data=color)

    def change_color(e):
        color_icon.icon_color = color_picker.color
        color_icon.data = color_picker.color
        e.control.page.close(d) #type:ignore
        e.control.page.update()

    def close_dialog(e):
        d.open = False
        d.update()

    d = ft.AlertDialog(
        content=color_picker,
        actions=[
            ft.TextButton("OK", on_click=change_color),
            ft.TextButton("Cancel", on_click=close_dialog),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=change_color,
    )

    return color_icon
# from flet.auth.providers import GoogleOAuthProvider as OAuthProvider


#NOLONGER#NS:{"mode"=color_mode, "theme"=theme_color, "stats".stat_name=[min,max,color, date,stat]}}
COLORS = [
    "red", 
    "pink", 
    "purple", 
    "deeppurple", 
    "indigo", 
    "blue", 
    "lightblue", 
    "teal", 
    "green", 
    "lightgreen", 
    "lime", 
    "yellow", 
    "amber", 
    "orange", 
    "deeporange", 
    "brown", 
    "grey", 
    "bluegrey", 
    "white", 
    "black"
]

is_valid_chart_name = lambda a: re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9 \-]*", a) != None
snake2normal = lambda a: a.replace("_", " ")
normal2snake = lambda a: a.replace(" ", "_")

async def get_search_bar(page:ft.Page):
    async def close_anchor(e):
        anchor.close_view(e.control.data)
        await handle_submit(..., e.control.data)

    def open_anchor(e):
        anchor.open_view()

    async def handle_submit(e):
        color = anchor.value or "Cyan"
        page.theme = ft.Theme(name2hex(color))
        anchor.bar_bgcolor = "#10"+name2hex(color)[1:]
        await page.client_storage.set_async(f"{NS}.theme", color)
        page.update()

    anchor = ft.SearchBar(
        value=await page.client_storage.get_async(f"{NS}.theme"),
        bar_bgcolor="#99"+name2hex(await page.client_storage.get_async(f"{NS}.theme"))[1:], #type:ignore
        view_elevation=4,
        divider_color=ft.colors.PRIMARY_CONTAINER,
        bar_hint_text="Choose Theme Color...",
        view_hint_text="Or Type Any Color (From CSS3)",
        on_submit=handle_submit,
        on_change=handle_submit,
        on_tap=open_anchor,
        controls=[
            ft.ListTile(title=ft.Text(i), on_click=close_anchor, data=i)
            for i in COLORS
        ],
    )
    
    return anchor
async def get_theme_switch(page:ft.Page):
    async def theme_changed(e):
        page.theme_mode = (
            ft.ThemeMode.DARK
            if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.ThemeMode.LIGHT
        )
        c.label = (
            "Light mode" if page.theme_mode == ft.ThemeMode.LIGHT else "Dark mode"
        )
        await page.client_storage.set_async(f"{NS}.mode", page.theme_mode.value)
        page.update()

    c = ft.Switch(on_change=theme_changed)
    c.label = (
            "Light mode" if page.theme_mode == ft.ThemeMode.LIGHT else "Dark mode"
        )
    return c

async def get_delete_button(page:ft.Page):
    def close_bs(e):
        page.close(bs)
    def open_bs(e):
        page.open(bs)
    
    def ask_delete_chart(e):
        async def delete_chart(e):
            close_bs1(...)
            # for i in await page.client_storage.get_keys_async(f"{NS}.chartdata.{e.control.data}"):
            #     print(await page.client_storage.remove_async(i))
            await page.client_storage.remove_async(f"{NS}.chartstats.{e.control.data}.min")
            await page.client_storage.remove_async(f"{NS}.chartstats.{e.control.data}.max")
            await page.client_storage.remove_async(f"{NS}.chartstats.{e.control.data}.color")
            await page.client_storage.remove_async(f"{NS}.chart.{e.control.data}")

            await page.client_storage.get_keys_async(f"{NS}")
        
            page.go("/"+page.route)
    
        def close_bs1(e):
            page.close(bs1)
        def open_bs1(e):
            page.open(bs1)
        bs1 = ft.AlertDialog(
            title=ft.Text("Are You Sure"),
            actions=[
                ft.ElevatedButton(text="Yes", data=e.control.data, color=ft.colors.RED, on_click=delete_chart),
                ft.ElevatedButton(text="No", on_click=close_bs1),
            ]
        )
        open_bs1(...)
        
    def set_buttons(*_):
        bs.content.controls = [
                ft.ElevatedButton(snake2normal(i), data=normal2snake(i), on_click=ask_delete_chart) for i in charts.chart_names
            ]
        page.update()
        
    charts = await getSortedCharts(page)
    
    bs = ft.AlertDialog(
        title=ft.Text("Delete Scales", style=ft.TextStyle(weight=ft.FontWeight.BOLD)),
        content=ft.Column(
                    tight=True,
                    expand=True,
                    scroll=ft.ScrollMode.ADAPTIVE
                ),
            actions=[
                ft.ElevatedButton(
                                "Back", on_click=close_bs
                )
            ],
            open=False,
        )
    charts.on_sort = set_buttons()
    set_buttons()
    return ft.ElevatedButton(
        "Delete Scales",
        on_click=open_bs,
        data=bs
        )

async def get_settings_button(page:ft.Page):
    async def open_bs(e):
        def close_bs(e):
            page.close(bs)
        bs = ft.AlertDialog(
            title=ft.Text("Settings", style=ft.TextStyle(weight=ft.FontWeight.BOLD)),
            content=ft.Column(
                        [
                            await get_theme_switch(page),
                            await get_search_bar(page),
                            await get_delete_button(page),
                        ],
                        tight=True,
                    ),
                actions=[
                    ft.ElevatedButton(
                                    "Back", on_click=close_bs
                    )
                ],
                open=False,
            )
        page.open(bs)
    return ft.ElevatedButton(
        "Settings",
        on_click=open_bs,
    )

def change_route(e:ft.ControlEvent):
    page:ft.Page = e.page
    nav_bar: ft.NavigationBar = e.control
    page.go("/"+normal2snake(nav_bar.destinations[nav_bar.selected_index].label)) #type:ignore

async def main(page:ft.Page):
    page.title = "Test Title 123"
    page.theme = ft.Theme(name2hex(await page.client_storage.get_async(f"{NS}.theme")))
    page.theme_mode = ft.ThemeMode(await page.client_storage.get_async(f"{NS}.mode"))
    def FixNavBar():
        toSnake = lambda a: normal2snake(a.label)
        snake = tuple(map(toSnake, nav_bar.destinations)) #type:ignore
        
        nav_bar.selected_index = snake.index(page.route.split("/")[-1])
    # print(await page.client_storage.get_keys_async(''))
    if not await page.client_storage.contains_key_async(NS):
        await page.client_storage.set_async(NS, True)
        await page.client_storage.set_async(f"{NS}.mode", "dark")
        await page.client_storage.set_async(f"{NS}.theme", "cyan")
        route = "/Add_Scale"
    if await page.client_storage.get_keys_async(f"{NS}.chart.") == []:
        route = "/Add_Scale"
    else:
        route = "/Add_Values"

    async def on_route_change(e:ft.RouteChangeEvent):
        page.views.clear()
        
        # if BOTTOM_PAGE:
        #     page.views.append(
        #         ft.View(
        #             BOTTOM_PAGE,
        #             [
        #                 ft.Text("Hello!"),
        #                 ft.Text("Your smth. is increasing")
        #             ],
        #             appbar=appbar,
        #             navigation_bar=nav_bar,
        #         )
        #     )
        
        # ft.View(
            # "route", 
            # [controls],
            # appbar=appbar,
            # navigation_bar=nav_bar
        # )
        # ft.View(page.route, [controls], appbar=appbar, navigation_bar=nav_bar)
        
        if "/"+e.route.lstrip("/") != e.route:
            page.go("/"+e.route.lstrip("/"))
        
        appbar.title = ft.Text(
            snake2normal(page.route.split("/")[-1]), 
            style=ft.TextStyle(weight=ft.FontWeight.BOLD))
        
        match page.route:
            case "/Add_Values":
                async def submit(e):
                    time = int(datetime.datetime.now().timestamp())
                    for i in sliders.controls:
                        text, slider = i.controls
                        name: str = normal2snake(text.value)
                        value: int = slider.value
                        await page.client_storage.set_async(f"{NS}.chartdata.{name}.{time}", value)
                        page.go("/View_Scales")
                        FixNavBar()
                
                async def place_slider(key):
                    min_y:int = await page.client_storage.get_async(f"{NS}.chartstats.{key}.min") #type:ignore
                    max_y:int = await page.client_storage.get_async(f"{NS}.chartstats.{key}.max") #type:ignore
                    color = await page.client_storage.get_async(f"{NS}.chartstats.{key}.color")
                    return ft.Row(
                            [
                                ft.Text(snake2normal(key)),
                                ft.Slider(
                                    (min_y+max_y)//2,
                                    min=min_y,
                                    max=max_y,
                                    divisions=max_y-min_y,
                                    label="{value}",
                                    thumb_color=color,
                                    active_color=color,
                                    expand=True,
                                ),
                            ]
                        )
                    
                async def place_sliders(charts):
                    sliders.controls = [await place_slider(key) for key in charts.chart_names]
                    page.update()
                    pass
                
                sliders = ft.Column([], expand=True, scroll=ft.ScrollMode.ADAPTIVE)
                charts = await getSortedCharts(page)
                charts.on_sort = place_sliders
                
                
                page.views.append(ft.View(
                    "route", 
                    [
                        charts.row,
                        sliders,
                        ft.Divider(),
                        ft.ElevatedButton(
                            "Submit",
                            on_click=submit
                        )
                    ],
                    appbar=appbar,
                    navigation_bar=nav_bar
                ))
                ensure_future(place_sliders(charts))
            case "/Add_Scale":
                async def submit(e):
                    if not is_valid_chart_name(name.value):
                        page.open(
                            ft.AlertDialog(
                                title=ft.Text(
                                    "Name Is Invalid",
                                    color=ft.colors.RED
                                ),
                                actions=[
                                    ft.ElevatedButton(
                                        "OK", 
                                        on_click=lambda e: e.control.page.close(e.control.parent))
                                ]
                            )
                        )
                        return
                    if round(range.start_value) == round(range.end_value):
                        page.open(
                            ft.AlertDialog(
                                title=ft.Text(
                                    "Start And End Values Are The Same",
                                    color=ft.colors.RED
                                ),
                                actions=[
                                    ft.ElevatedButton(
                                        "OK", 
                                        on_click=lambda e: e.control.page.close(e.control.parent))
                                ]
                            )
                        )
                        return
                    if await page.client_storage.contains_key_async(f"{NS}.chart.{name.value}"):
                        page.open(
                            ft.AlertDialog(
                                title=ft.Text(
                                    "Can Not Have Duplicate Names",
                                    color=ft.colors.RED
                                ),
                                actions=[
                                    ft.ElevatedButton(
                                        "OK", 
                                        on_click=lambda e: e.control.page.close(e.control.parent))
                                ]
                            )
                        )
                        return
                    await page.client_storage.set_async(f"{NS}.chartstats.{normal2snake(name.value)}.min", round(range.start_value)) 
                    await page.client_storage.set_async(f"{NS}.chartstats.{normal2snake(name.value)}.max", round(range.end_value)) 
                    await page.client_storage.set_async(f"{NS}.chartstats.{normal2snake(name.value)}.color", color.data) 
                    await page.client_storage.set_async(f"{NS}.chart."+normal2snake(name.value), [round(range.start_value), round(range.end_value), color.data])
                    page.go("/Add_Values")
                    FixNavBar()
                name = ft.TextField(label="Enter Chart Name...",hint_text="Sleep Time")
                range = ft.RangeSlider(1, 10, min=0, max=100, 
                                        label="{value}", divisions=100)
                color = ColorPicker("#38938a")
                page.views.append(ft.View(
                    page.route, 
                    [
                        name,
                        range,
                        color,
                        ft.Divider(),
                        ft.ElevatedButton("Add Chart", on_click=submit)
                    ], 
                    appbar=appbar, 
                    navigation_bar=nav_bar
                ))
            case "/View_Scales":
                async def get_charts(*_):
                    async def get_chart(key):
                        name = snake2normal(key)
                        min_y:int = await page.client_storage.get_async(f"{NS}.chartstats.{key}.min") #type:ignore
                        max_y:int = await page.client_storage.get_async(f"{NS}.chartstats.{key}.max") #type:ignore
                        color = await page.client_storage.get_async(f"{NS}.chartstats.{key}.color")
                        values = getChartValues(page, key)
                                                
                        try:
                            data = ft.LineChartData(
                                            [
                                                ft.LineChartDataPoint(x=i[0], y=i[1], tooltip=f"{datetime.datetime.fromtimestamp(int(i[0])).strftime(DATE_FORMAT)} - {round(i[1])}") async for i in values
                                            ],
                                            stroke_width=3,
                                            color=color,
                                            curved=True,
                                            stroke_cap_round=True,
                                            point=True,
                                        )
                            
                            chart = ft.LineChart(
                                    [
                                        data
                                    ],
                                    data=(min_y, max_y),
                                    border=ft.border.all(3, ft.colors.with_opacity(0.2, ft.colors.ON_SECONDARY_CONTAINER)),
                                    bgcolor=ft.colors.ON_SECONDARY,
                                    min_y=min_y, max_y=max_y
                                )
                            
                            return ft.Column(
                                    [
                                        ft.Text(name),
                                        chart,
                                        # ft.Row(
                                        #     [
                                        #         # get_add_record_button(page, chart, key),
                                        #         # get_delete_chart_button(page, chart, key),
                                        #     ]
                                        # )
                                    ]
                                )
                            
                        except Exception as exc:
                            print(exc)
                            return ft.Column([ft.Text("Unable to load table")]) 
                    
                    charts = [await get_chart(a) for a in chart_sort.chart_names]
                    
                    if _:
                        charts_.controls = charts
                        page.update()
                    return charts
                
                chart_sort = await getSortedCharts(page)
                
                charts_ = ft.Column(
                                scroll=ft.ScrollMode.ADAPTIVE,
                                expand=True
                )
                charts_.controls = await get_charts() #type:ignore
                chart_sort.on_sort = get_charts
                
                
                page.views.append(
                    ft.View(
                        page.route,
                        [
                            chart_sort.row,
                            charts_,
                        ],
                        appbar=appbar,
                        navigation_bar=nav_bar,
                    )
                )
            case "/":
                pass
            case a:
                raise KeyError(f"Page '{a}' not found")
                pass
        
        page.update()
    
        
    appbar = ft.AppBar(
            actions=[
                await get_settings_button(page)
            ]
        )
    
    
    nav_bar = ft.NavigationBar(
        [
            ft.NavigationBarDestination(
                "Add Values",
                icon=ft.icons.ADD_BOX_ROUNDED,
                selected_icon=ft.icons.ADD_BOX_OUTLINED
                ),
            ft.NavigationBarDestination(
                "Add Scale",
                icon=ft.icons.NOTE_ADD,
                selected_icon=ft.icons.NOTE_ADD_OUTLINED
                ),
            ft.NavigationBarDestination(
                "View Scales", 
                icon=ft.icons.INSERT_CHART_ROUNDED,
                selected_icon=ft.icons.INSERT_CHART_OUTLINED_ROUNDED
                ),
        ],
        on_change=change_route
    )
    
    page.on_route_change = on_route_change
    
    page.go(route)
    
    FixNavBar()

    

ft.app(target=main)

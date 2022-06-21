from random import random
from magicgui import magicgui, type_map
from magicgui.widgets import Container

def get_a(data):
    print(type(data), data)
    return random() + 1000

type_map.register_type(int, widget_type='Slider', max=10)

@magicgui(auto_call=True, result_widget=True)
def main(x: int):
    return x * 5


@magicgui(auto_call=True, result_widget=True)
def main2(a, x=8, y=5):
    return a + x + y
main2.a.bind(get_a)

app = Container(widgets=[main, main2], labels=False)
app.show(run=True)
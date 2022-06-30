
from traitlets import HasTraits, validate, Int

from .utils import PrintableTraits



class CropState(HasTraits, PrintableTraits):
    x0 = Int(default_value=0)
    x1 = Int(default_value=50)
    x_max = Int(default_value=100)
    y0 = Int(default_value=0)
    y1 = Int(default_value=60)
    y_max = Int(default_value=80)

    @validate('x0')
    def _check_x0(self, proposal):
        x0 = proposal['value']
        if x0 >= self.x1:
            return self.x0
        return x0

    @validate('x1')
    def _check_x1(self, proposal):
        x1 = proposal['value']
        if self.x0 >= x1:
            return self.x1
        return x1

    @validate('y0')
    def _check_y0(self, proposal):
        y0 = proposal['value']
        if y0 >= self.y1:
            return self.y0
        return y0

    @validate('y1')
    def _check_y1(self, proposal):
        y1 = proposal['value']
        if self.y0 >= y1:
            return self.y1
        return y1

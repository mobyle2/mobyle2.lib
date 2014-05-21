# -*- coding: utf-8 -*-


class EvalBoolFactory(object):

    def __init__(self, values={}):
        self.values = {}

    def test(self, expr):
        if not(expr):
            return True
        result = True
        # 'variable'
        # means variable is truthy
        if isinstance(expr, basestring):
            return bool(self.values[expr])
        # {}
        # return true if all contained key/value tests are true
        elif isinstance(expr, dict):
            for key, value in expr.items():
                # iterate tests in the dict
                if key in self.values.keys():
                    # {'x':1} return true if values['x']==1
                    if isinstance(value, int) or isinstance(value, basestring)\
                        or isinstance(value, float) or isinstance(value, bool):
                            if self.values[key] != value:
                                result = False
                # comparison operators
                elif key == '#gt':
                    result = self.values[key] > value[key]
                elif key == '#gte':
                    result = self.values[key] >= value[key]
                elif key == '#lt':
                    result = self.values[key] < value[key]
                elif key == '#lte':
                    result = self.values[key] <= value[key]
                elif key == '#in':
                    result = self.values[key] in value[key]
                elif key == '#ne':
                    result = self.values[key] != value[key]
                elif key == '#nin':
                    result = self.values[key] not in value[key]
                # logical operators
                elif key == '#or':
                    inner_result = True
                    for inner_test in value[key]:
                        inner_result = self.test(inner_test)
                        if inner_result is True:
                            result = True
                            break
                    result = True
                elif key == '#and':
                    inner_result = True
                    for inner_test in value[key]:
                        inner_result = self.test(inner_test)
                        if inner_result is False:
                            result = False
                            break
                    result = True
                elif key == '#not':
                    result = not(self.test(value[key]))
                elif key == '#nor':
                    inner_result = True
                    for inner_test in value[key]:
                        inner_result = not(self.test(inner_test))
                        if inner_result is False:
                            result = False
                            break
                # break on first unmet condition
                if result is False:
                    break
        # []
        # return false on first condition not met
        elif isinstance(expr, list):
            for test_item in expr:
                result = self.test(test_item)
                if result is False:
                    break
        return result


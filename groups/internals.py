import copy



class GroupDummy(object):
    
    def __nonzero__(self):
        return False


class GroupRequestHelper(object):
    
    def __init__(self, request, group):
        self.request = request
        self.group = group
    
    def __deepcopy__(self, memo):
        obj = copy.copy(self)
        for k, v in self.__dict__.iteritems():
            if k == "request":
                continue
            setattr(obj, k, copy.deepcopy(v, memo))
        obj.request = self.request
        memo[id(self)] = obj
        return obj
    
    def user_is_member(self):
        if not self.request.user.is_authenticated():
            is_member = False
        else:
            if self.group:
                is_member = self.group.user_is_member(self.request.user)
            else:
                is_member = True
        return is_member

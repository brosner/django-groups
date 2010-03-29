from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils.functional import curry

from groups.internals import GroupDummy, GroupRequestHelper



class GroupAwareMiddleware(object):
    
    def process_view(self, request, view, view_args, view_kwargs):
        
        bridge = view_kwargs.pop("bridge", None)
        
        if bridge:
            try:
                group = bridge.get_group(view_kwargs)
            except ObjectDoesNotExist:
                raise Http404
        else:
            group = GroupDummy()
        
        # attach a request helper
        group.request = GroupRequestHelper(request, group)
        
        request.group = group
        request.bridge = bridge
        
        return None

from functools import wraps

from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def patient_access_required(function):
    """ this function is a decorator used to authorize if a user is tutor """

    def wrap(request, *args, **kwargs):
        if (
            request.user.role == "Patient"

        ):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return wrap


def staff_access_required(function):
    """ this function is a decorator used to authorize if a user is admin """

    def wrap(request, *args, **kwargs):
        if request.user.role == "ADMIN" or request.user.is_superuser:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return wrap





# Note:
# import this line in views
# from common.access_decorators_mixins import survivor_access_required, volunteer_access_required, staff_access_required
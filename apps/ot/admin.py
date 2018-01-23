from django.contrib import admin
from .models.club import *
from .models.user import *
from .models.vote import *


admin.site.register(Club)
admin.site.register(Freshman)
admin.site.register(Image)
admin.site.register(VotePolicy)

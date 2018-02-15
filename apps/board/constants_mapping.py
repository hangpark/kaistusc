
from .forms import PostForm, ProjectPostForm, DebateForm
from .models import Post, DebatePost, ProjectPost
from .constants import *

mapping_model = {
	BOARD_ROLE_DEFAULT:Post,
	BOARD_ROLE_PROJECT:ProjectPost,
	BOARD_ROLE_DEBATE:DebatePost
}

mapping_form = {
	BOARD_ROLE_DEFAULT:PostForm,
	BOARD_ROLE_PROJECT:ProjectPostForm,
	BOARD_ROLE_DEBATE:DebateForm
}
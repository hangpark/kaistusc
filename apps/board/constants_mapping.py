
from .forms import PostForm, ProjectPostForm, DebatePostForm
from .models import Post, DebatePost, ProjectPost
from .constants import *

MAP_MODEL_POST = {
	BOARD_ROLE_DEFAULT:Post,
	BOARD_ROLE_PROJECT:ProjectPost,
	BOARD_ROLE_DEBATE:DebatePost,
    BOARD_ROLE_PLANBOOK:Post
}

MAP_FORM_POST = {
	BOARD_ROLE_DEFAULT:PostForm,
	BOARD_ROLE_PROJECT:ProjectPostForm,
	BOARD_ROLE_DEBATE:DebatePostForm,
    BOARD_ROLE_PLANBOOK:PostForm
}
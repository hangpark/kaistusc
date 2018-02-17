
from .forms import PostForm, ProjectPostForm, DebatePostForm
from .models import Post, DebatePost, ProjectPost
from .constants import *

MAP_MODEL_POST = {
	BOARD_ROLE['DEFAULT']:Post,
	BOARD_ROLE['PROJECT']:ProjectPost,
	BOARD_ROLE['DEBATE']:DebatePost,
    BOARD_ROLE['PLANBOOK']:Post
}

MAP_FORM_POST = {
	BOARD_ROLE['DEFAULT']:PostForm,
	BOARD_ROLE['PROJECT']:ProjectPostForm,
	BOARD_ROLE['DEBATE']:DebatePostForm,
    BOARD_ROLE['PLANBOOK']:PostForm
}
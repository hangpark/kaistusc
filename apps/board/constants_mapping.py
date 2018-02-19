
from .forms import PostForm, ProjectPostForm, DebatePostForm, WorkhourPostForm, PlanbookPostForm
from .models import Post, DebatePost, ProjectPost, Product
from .constants import *

MAP_MODEL_POST = {
	BOARD_ROLE['DEFAULT']:Post,
	BOARD_ROLE['PROJECT']:ProjectPost,
	BOARD_ROLE['DEBATE']:DebatePost,
	BOARD_ROLE['PLANBOOK']:Post,
	BOARD_ROLE['ARCHIVING']:Post,
	BOARD_ROLE['WORKHOUR']:Post,
    BOARD_ROLE['STORE']:Product,
}

MAP_FORM_POST = {
	BOARD_ROLE['DEFAULT']:PostForm,
	BOARD_ROLE['PROJECT']:ProjectPostForm,
	BOARD_ROLE['DEBATE']:DebatePostForm,
	BOARD_ROLE['ARCHIVING']:PostForm,
	BOARD_ROLE['PLANBOOK']:PlanbookPostForm,
	BOARD_ROLE['WORKHOUR']:WorkhourPostForm,
	BOARD_ROLE['STORE']:PostForm,
}
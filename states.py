from aiogram.dispatcher.filters.state import StatesGroup, State


class States_admin(StatesGroup):
    get_phone = State()
    # ------------------------------->
    Categories = State()
    # ------------------------------->
    Products = State()
    # ------------------------------->
    my_adress = State()
    #-------------------------------->
    filials = State()
    #-------------------------------->
    comment =State()

    #-------------------------------->
    admin = State()
    # ------------------------------>Admin
    check_type = State()
    # ------------------------------>Text
    ask_text = State()
    check_answer_text = State()
    # ------------------------------>Photo
    submit_image = State()
    check_answer_photo = State()
    # ------------------------------>Video
    submit_video = State()
    check_answer_video = State()
    # ------------------------------> Photo +text
    mailing_photo = State()
    mailing_tex = State()
    submit_mailing_photo = State()
    # ------------------------------>Video + text
    mailing_text_video = State()
    check_mailing_video_text = State()
    submit_mailing_video_text = State()

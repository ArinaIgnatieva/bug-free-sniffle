@app.route('/calendar', methods=['POST', 'GET'])
def calendar():
    email = request.cookies.get("email")
    if email not in all_users:
        response = make_response(render_template('index.html'))
        response.delete_cookie('email')
        return response
    return render_template('calendar.html', events=all_users[email].events)


def get_date_for_event(date_str: str) -> str | None:
    datetime_list = date_str.strip().split(" ")
    try:
        datetime.strptime(datetime_list[0], '%Y-%m-%d')
        if len(datetime_list) > 1:
            datetime.strptime(datetime_list[1], '%H:%M')
            return datetime_list[0] + " " + datetime_list[1]
        else:
            return datetime_list[0]
    except ValueError:
        return None


@app.route('/add_new_event', methods=['GET', "POST"])
def add_new_event():
    email = request.cookies.get("email")
    if email not in all_users:
        response = make_response(render_template('index.html'))
        response.delete_cookie('email')
        return response
    if request.method == "POST":
        err_msg = None
        title = request.form.get('title')
        if title == '':
            err_msg = "Вы забыли вписать название задачи"
        description = request.form.get('description')
        color = request.form.get('color')
        if color == '':
            err_msg = "Заполните поле 'цвет'"
        file = request.form.get('file')  # TODO: бесполезный файл
        start = request.form.get('start')
        if start == '':  # TODO: много траблов с временем
            err_msg = "Заполните поле 'Дата и время начала'"
        start = get_date_for_event(start)
        if not start:
            err_msg = "Заполните дату 'начала' по формату 'гггг-мм-дд чч:мм'"
        end = request.form.get('end')
        url = request.form.get('url')  # TODO: бесполезный ссылка
        if end == '':
            end = start
        else:
            end = get_date_for_event(end)
            if not end:
                err_msg = "Заполните дату 'окончания' по формату 'гггг-мм-дд чч:мм'"
        if err_msg:
            return render_template("newEvent.html", message=err_msg)

        all_users[email].new_event(
            title=title,
            description=description,
            color=color,
            file=file,
            start=start,
            end=end,
            url=url,
        )
        return render_template('calendar.html', events=all_users[email].events)
    else:
        return render_template("newEvent.html")


@app.route('/event/<event_id>', methods=['GET', "POST"])
def event(event_id):
    email = request.cookies.get("email")
    if email not in all_users:
        response = make_response(render_template('index.html'))
        response.delete_cookie('email')
        return response
    if request.method == "POST":
        err_msg = None
        title = request.form.get('title')
        if title == '':
            err_msg = "Вы забыли вписать название задачи"
        description = request.form.get('description')
        color = request.form.get('color')
        if color == '':
            err_msg = "Заполните поле 'цвет'"
        file = request.form.get('file')  # TODO: бесполезный файл
        start = request.form.get('start')
        if start == '':  # TODO: много траблов с временем
            err_msg = "Заполните поле 'Дата и время начала'"
        start = get_date_for_event(start)
        if not start:
            err_msg = "Заполните дату 'начала' по формату 'гггг-мм-дд чч:мм'"
        end = request.form.get('end')
        url = request.form.get('url')  # TODO: бесполезный ссылка
        if end == '':
            end = start
        else:
            end = get_date_for_event(end)
            if not end:
                err_msg = "Заполните дату 'окончания' по формату 'гггг-мм-дд чч:мм'"
        if err_msg:
            return render_template("newEvent.html", message=err_msg)

        all_users[email].update_event(
            event_id=event_id,
            title=title,
            description=description,
            color=color,
            file=file,
            start=start,
            end=end,
            url=url,
        )
        return render_template('calendar.html', events=all_users[email].events)
    else:
        return render_template(
            "eventDescription.html", event_id=event_id,
            event=all_users[email].user_events.get_all_event(event_id)
        )


@app.route('/del_event/<event_id>')
def del_event(event_id):
    email = request.cookies.get("email")
    if email not in all_users:
        response = make_response(render_template('index.html'))
        response.delete_cookie('email')
        return response
    all_users[email].del_event(event_id)
    return render_template('calendar.html', events=all_users[email].events)

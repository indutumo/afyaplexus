from celery import shared_task

from .models import (
    Visitor,
    Session,
    PageView,
    ClickEvent,
    SearchEvent,
    FunnelEvent
)


@shared_task
def log_page_view(data):
    visitor = Visitor.objects.get(id=data['visitor_id'])
    session = Session.objects.get(id=data['session_id'])

    PageView.objects.create(
        visitor=visitor,
        session=session,
        path=data['path'],
        full_url=data.get('full_url'),
        view_name=data.get('view_name'),
        method=data.get('method'),
        referrer=data.get('referrer')
    )


@shared_task
def log_click_event(data):
    visitor = Visitor.objects.get(id=data['visitor_id'])
    session = Session.objects.get(id=data['session_id'])

    ClickEvent.objects.create(
        visitor=visitor,
        session=session,
        page=data['page'],
        event_type=data['event_type'],
        label=data.get('label'),
        x=data.get('x'),
        y=data.get('y'),
        screen_width=data.get('screen_width'),
        screen_height=data.get('screen_height')
    )


@shared_task
def log_search_event(data):
    visitor = Visitor.objects.get(id=data['visitor_id'])
    session = Session.objects.get(id=data['session_id'])

    SearchEvent.objects.create(
        visitor=visitor,
        session=session,
        query=data['query'],
        page=data['page']
    )


@shared_task
def log_funnel_event(data):
    visitor = Visitor.objects.get(id=data['visitor_id'])
    session = Session.objects.get(id=data['session_id'])

    FunnelEvent.objects.create(
        visitor=visitor,
        session=session,
        funnel_name=data['funnel_name'],
        step=data['step']
    )
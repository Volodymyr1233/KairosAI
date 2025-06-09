import pytest
from AI.ai_handler import ai_parse_text


def test_ai_parse_text_add_event():
    user_input = "dodaj na jutro spotkanie z Mateuszem od 10 do 12"
    result = ai_parse_text(user_input)

    assert result is not None
    assert "event_type" in result
    assert result["event_type"] == "Add" or result["event_type"] == "ADD"
    assert "event_name" in result
    assert "data_start" in result
    assert "data_end" in result
    assert isinstance(result["attendees_emails"], list)
    assert all(isinstance(email, str) for email in result["attendees_emails"])


def test_ai_parse_text_edit_event():
    user_input = "zmień nazwę spotkania na jutrzejszym wydarzeniu"
    result = ai_parse_text(user_input)

    assert result is not None
    assert "event_type" in result
    assert result["event_type"].lower() == "edit"
    assert "new_event_name" in result


def test_ai_parse_text_invalid_emails_filtered():
    user_input = "dodaj spotkanie z mailami: valid@example.com, invalid-email"
    result = ai_parse_text(user_input)

    assert result is not None
    assert "attendees_emails" in result
    for email in result["attendees_emails"]:
        assert "@" in email and "." in email

    for email in result["new_attendees_emails"]:
        assert "@" in email and "." in email


def test_ai_parse_text_add_event_full():
    user_input = "dodaj spotkanie zespołu na 2025-06-12 od 14:00 do 15:30 z opisem 'Omówienie projektu' w biurze, kolor niebieski, przypomnienie 30 minut przed, uczestnicy jan@example.com, anna@example.com"
    result = ai_parse_text(user_input)

    assert result is not None

    assert result["event_type"].lower() == "add"

    assert isinstance(result["event_name"], str) and len(result["event_name"]) > 0

    if result.get("event_description") is not None:
        assert isinstance(result["event_description"], str)

    from dateutil.parser import parse
    parse(result["data_start"])
    parse(result["data_end"])


    assert result.get("new_data_start") is None
    assert result.get("new_data_end") is None


    assert isinstance(result.get("location"), (str, type(None)))


    remind = result.get("remind_minutes")
    assert remind is None or (isinstance(remind, int) and remind > 0)


    valid_colors = {
        "jasnoniebieski", "miętowy", "fioletowy", "łososiowy", "żółty",
        "pomarańczowy", "turkusowy", "szary", "niebieski", "zielony", "czerwony"
    }
    if result.get("event_color") is not None:
        assert result["event_color"] in valid_colors

    assert isinstance(result.get("attendees_emails"), list)
    for mail in result["attendees_emails"]:
        assert isinstance(mail, str)
        assert "@" in mail and "." in mail

    new_attendees = result.get("new_attendees_emails")
    assert new_attendees is None or isinstance(new_attendees, list)


def test_ai_parse_text_edit_event_full():
    user_input = "edytuj wydarzenie: zmień nazwę na 'Spotkanie strategiczne', zmień datę na 2025-07-01 od 09:00 do 11:00, zmień kolor na czerwony, dodaj uczestnika piotr@example.com, przypomnienie 15 minut"
    result = ai_parse_text(user_input)

    assert result is not None
    assert result["event_type"].lower() == "edit"

    assert isinstance(result.get("event_name"), str)
    assert isinstance(result.get("new_event_name"), str)
    assert len(result["new_event_name"]) > 0

    from dateutil.parser import parse
    parse(result["new_data_start"])
    parse(result["new_data_end"])

    valid_colors = {
        "jasnoniebieski", "miętowy", "fioletowy", "łososiowy", "żółty",
        "pomarańczowy", "turkusowy", "szary", "niebieski", "zielony", "czerwony"
    }
    if result.get("new_event_color") is not None:
        assert result["new_event_color"] in valid_colors

    new_attendees = result.get("new_attendees_emails")
    assert isinstance(new_attendees, list)
    for mail in new_attendees:
        assert isinstance(mail, str)
        assert "@" in mail and "." in mail

    remind = result.get("new_remind_minutes")
    assert remind is None or (isinstance(remind, int) and remind > 0)

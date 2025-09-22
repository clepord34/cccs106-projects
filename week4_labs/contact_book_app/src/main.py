# main.py
import flet as ft
from database import init_db
from app_logic import display_contacts, add_contact, theme_change

def main(page: ft.Page):
    page.title = "Contact Book"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_width = 400
    page.window_height = 600
    page.theme_mode = ft.ThemeMode.SYSTEM

    db_conn = init_db()

    name_input = ft.TextField(label="Name", width=350)
    phone_input = ft.TextField(label="Phone", width=350)
    email_input = ft.TextField(label="Email", width=350)

    inputs = (name_input, phone_input, email_input)

    contacts_list_view = ft.ListView(expand=1, spacing=10, auto_scroll=True)

    add_button = ft.ElevatedButton(
        text="Add Contact",
        on_click=lambda e: add_contact(page, inputs, contacts_list_view, db_conn)
    )

    theme_change_switch = ft.Switch(label="Light theme", on_change=lambda e: theme_change(page, theme_change_switch))
    search_box = ft.TextField(label="Search", width=350, on_change=lambda e: display_contacts(page, contacts_list_view, db_conn, search_query=e.control.value))
    
    page.add(
        ft.Column(
            [
                ft.Text("Enter Contact Details:", size=20, weight=ft.FontWeight.BOLD),
                theme_change_switch,
                name_input,
                phone_input,
                email_input,
                add_button,
                ft.Divider(),
                ft.Text("Contacts:", size=20, weight=ft.FontWeight.BOLD),
                search_box,
                contacts_list_view,
            ]  
        )
    )
    display_contacts(page, contacts_list_view, db_conn, search_query=None)

if __name__ == "__main__":
    ft.app(target=main)
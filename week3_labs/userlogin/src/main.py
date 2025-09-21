import flet as ft
import mysql.connector
from mysql.connector import Error
import db_connection as db

def main(page: ft.Page):
    def login_click(e):
        input_username = username_box.value
        input_password = password_box.value

        success_dialog = ft.AlertDialog(
            icon=ft.Icon(name=ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN),
            title=ft.Text("Login Successful", text_align=ft.TextAlign.CENTER,color=ft.Colors.BLACK),
            content=ft.Text(f"Welcome, {input_username}", text_align=ft.TextAlign.CENTER, color=ft.Colors.BLACK),
            alignment=ft.alignment.center,
            actions=[ft.TextButton("OK", on_click=lambda e: page.close(success_dialog))],
            bgcolor=ft.Colors.WHITE,
            )
        failure_dialog = ft.AlertDialog(
            icon=ft.Icon(name=ft.Icons.ERROR, color=ft.Colors.RED),
            title=ft.Text("Login Failed", text_align=ft.TextAlign.CENTER,color=ft.Colors.BLACK),
            content=ft.Text(f"Invalid username or password", text_align=ft.TextAlign.CENTER, color=ft.Colors.BLACK),
            alignment=ft.alignment.center,
            actions=[ft.TextButton("OK", on_click=lambda e: page.close(failure_dialog))],
            bgcolor=ft.Colors.WHITE,
            )
        invalid_input_dialog = ft.AlertDialog(
            icon=ft.Icon(name=ft.Icons.INFO, color=ft.Colors.BLUE),
            title=ft.Text("Input Error", text_align=ft.TextAlign.CENTER,color=ft.Colors.BLACK),
            content=ft.Text(f"Please enter username and password", text_align=ft.TextAlign.CENTER, color=ft.Colors.BLACK),
            alignment=ft.alignment.center,
            actions=[ft.TextButton("OK", on_click=lambda e: page.close(invalid_input_dialog))],
            bgcolor=ft.Colors.WHITE,
            )
        database_error_dialog = ft.AlertDialog(
            title=ft.Text("Database Error",color=ft.Colors.BLACK),
            content=ft.Text(f"An error occurred while connecting to the database", color=ft.Colors.BLACK),
            alignment=ft.alignment.center,
            actions=[ft.TextButton("OK", on_click=lambda e: page.close(database_error_dialog))],
            bgcolor=ft.Colors.WHITE,
            )
        
        try:
            connection = db.connect_db()
            cursor = connection.cursor()

            sql = "SELECT id, username, password FROM users WHERE username = %s AND password = %s"
            cursor.execute(sql, (input_username, input_password))
            result = cursor.fetchone()

            if not input_username or not input_password:
                page.open(invalid_input_dialog)
            elif result:
                page.open(success_dialog)
            elif not result:
                page.open(failure_dialog)
            
            page.update()

        except Error as err:
            print(f"Error: {err}")
            page.open(database_error_dialog)
        finally:
            # Close the connection
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection closed.")

    page.window.center()
    page.window.frameless = True
    page.title = "User Login"
    page.window.height = 350
    page.window.width = 400
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.Colors.AMBER_ACCENT

    username_box = ft.TextField(label="User name",
                    hint_text="Enter your user name",
                    helper_text="This is your unique identifier",
                    width=300,
                    autofocus=True,
                    icon=ft.Icon(ft.Icons.PERSON),
                    bgcolor=ft.Colors.LIGHT_BLUE_ACCENT)
    
    password_box = ft.TextField(label="Password",
                    hint_text="Enter your password",
                    helper_text="This is your secret key",
                    width=300,
                    autofocus=True,
                    password=True,
                    can_reveal_password=True,
                    icon=ft.Icon(ft.Icons.PASSWORD),
                    bgcolor=ft.Colors.LIGHT_BLUE_ACCENT,)
    
    login_button = ft.ElevatedButton(text="Login", on_click=login_click, width=100, icon=ft.Icons.LOGIN)

    page.add(
        ft.Text(value="User Login", text_align=ft.MainAxisAlignment.CENTER, size=20, weight="bold", font_family="Arial"),
        ft.Container(ft.Column([username_box, password_box],
                               spacing=20,)),
        ft.Container(content=login_button, alignment=ft.alignment.top_right, margin=ft.margin.only(0, 20, 40, 0)),
    )

ft.app(target=main)
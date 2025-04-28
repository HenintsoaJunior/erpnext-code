import frappe
from frappe.sessions import get_session

sid = "94e5e15678b36d9e594a23e4fdf591e9ae3dd66650e04406816335a6"
session_obj = get_session(sid)

session_data = session_obj.get_session_record()
print("User:", session_data.user)
print("Status:", session_data.status)

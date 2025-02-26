from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from Student import Student
# from student_Dung import Dung
# from student_Long import Long
from student_Ekalat import Ekalat
# from student_Linh import Linh
# from student_Dat import Dat
# from student_thanakone import Thanakone
# from student_Tham import Tham
# from student_Vu import Vu

# Create instances of studentsI
students = {
    # "Dung": Dung(),
    # "Long": Long(),
    "Ekalat": Ekalat(),
    # "Dat": Dat(),
    # "Linh": Linh(),
    # "Tham": Tham(),
    # "Thanakone": Thanakone(),
    # "Vu": Vu()
}


# Escape special characters for MarkdownV2
def escape_markdown(text: str) -> str:
    special_chars = r"_*[]()~`>#+-=|{}.!\\"
    return "".join(f"\\{char}" if char in special_chars else char for char in text)

# Start Command with Help Instructions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = escape_markdown("""
🤖 *Welcome to the Student Info Bot!*

You can interact with the following commands:

/start \\- Display this help message.
/student <name> \\- Get details about a specific student. Example: `/student Dung`
/list_students \\- List all available students.

🔍 *Example Usage:*
- `/student Dung`
- `/student An`

Type a command to begin!
""")
    await update.message.reply_text(help_message, parse_mode="MarkdownV2")


async def handle_student_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Xử lý lệnh dạng: /student <Tên SV> <lệnh> [tham số 1] [tham số 2] ...
    Ví dụ: 
    - /student Long speak
    - /student Long stock FPT
    """
    print(f"Received command: {context.args}")
    try:
        # Kiểm tra đủ tham số tối thiểu (tên sv và lệnh)
        if len(context.args) < 2:
            await update.message.reply_text("Cú pháp không đúng. Sử dụng: /student <Tên SV> <lệnh> [tham số...]")
            return

        student_name = context.args[0]
        command = context.args[1].lower()
        # Lấy các tham số còn lại nếu có
        params = context.args[2:] if len(context.args) > 2 else []

        # Kiểm tra nếu lệnh là 'stock' nhưng không có mã chứng khoán
        if command == "stock" and len(params) < 1:
            await update.message.reply_text("Cú pháp không đúng. Sử dụng: /student <Tên SV> stock <mã_chứng_khoán>")
            return
        
        # Kiểm tra sinh viên có trong danh sách không
        if student_name not in students:
            await update.message.reply_text(f"Không tìm thấy sinh viên {student_name}")
            return
            
        student = students[student_name]
        
        # Kiểm tra và gọi phương thức tương ứng
        if hasattr(student, command):
            method = getattr(student, command)
            
            try:
                # Gọi method với các tham số nếu có
                if params:
                    result = method(*params)
                else:
                    result = method()
                    
                await update.message.reply_text(result)
            except TypeError as e:
                # Xử lý lỗi số lượng tham số không đúng
                await update.message.reply_text(f"Lỗi: Số lượng tham số không đúng cho lệnh {command}")
            except Exception as e:
                await update.message.reply_text(f"Lỗi khi thực thi lệnh {command}: {str(e)}")
        else:
            await update.message.reply_text(f"Không tìm thấy lệnh {command} cho sinh viên {student_name}")


    except Exception as e:
        await update.message.reply_text(f"Lỗi: {str(e)}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Hiển thị danh sách các lệnh có thể dùng cho mỗi student
    """
    try:
        # Lấy một instance của Student để kiểm tra các method có sẵn
        sample_student = students["Dung"]
        
        # Lấy tất cả các method của class (không lấy các method bắt đầu bằng '_')
        methods = [method for method in dir(sample_student) 
                  if not method.startswith('_') and callable(getattr(sample_student, method))]
        
        # Tạo message help
        help_text = "📚 *Danh sách các lệnh có thể sử dụng:*\n\n"
        help_text += "Cú pháp: `/student <tên_sv> <lệnh>`\n\n"
        help_text += "*Các lệnh:*\n"
        for method in methods:
            help_text += f"• `{method}` - Gọi phương thức {method} của sinh viên\n"
        
        help_text += "\n*Ví dụ:*\n"
        help_text += "• `/student Vu speak`\n"
        help_text += "• `/student ABC name`\n\n"
        
        help_text += "*Danh sách sinh viên:*\n"
        for student_name in students.keys():
            help_text += f"• {student_name}\n"
        
        # Escape các ký tự đặc biệt cho MarkdownV2
        help_text = escape_markdown(help_text)
        
        await update.message.reply_text(help_text, parse_mode="MarkdownV2")
        
    except Exception as e:
        await update.message.reply_text(f"Lỗi: {str(e)}")


# Main function to run the bot
# Done! Congratulations on your new bot. You will find it at t.me/K64_chuyende2_bot. You can now add a description, about section and profile picture for your bot, see /help for a list of commands. By the way, when you've finished creating your cool bot, ping our Bot Support if you want a better username for it. Just make sure the bot is fully operational before you do this.
#
# Use this token to access the HTTP API:
# 7718470610:AAFSLzaJjsLk5hgFkV86WX8MbhEcdiILtnY
# Keep your token secure and store it safely, it can be used by anyone to control your bot.
#
# For a description of the Bot API, see this page: https://core.telegram.org/bots/api
def main():
    bot_token = "7705072328:AAElGoUVLaXNnbwsMyBg59tWOCXNdVtHkz4"
    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("student", handle_student_command))
    app.add_handler(CommandHandler("help", help_command))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
    

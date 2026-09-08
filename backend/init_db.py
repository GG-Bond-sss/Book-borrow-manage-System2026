"""数据库初始化脚本。

首次运行时执行：python init_db.py
会创建表结构并插入初始数据（管理员账号、预置分类、测试图书）。
"""
import sys
import os
from datetime import datetime, timedelta

# 确保能导入项目模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base, SessionLocal
from models.user import User
from models.category import Category
from models.book import Book
from models.borrow_record import BorrowRecord
from services.auth_service import hash_password
from config import settings


def init_database():
    """初始化数据库。"""
    print("正在创建表结构...")
    Base.metadata.create_all(bind=engine)
    print("表结构创建完成。")

    db = SessionLocal()
    try:
        # 1. 创建管理员账号
        if not db.query(User).filter(User.username == settings.ADMIN_USERNAME).first():
            admin = User(
                username=settings.ADMIN_USERNAME,
                password=hash_password(settings.ADMIN_PASSWORD),
                role="admin",
                real_name="管理员",
                phone="13800000000",
                email="admin@library.com",
            )
            db.add(admin)
            print(f"管理员账号创建成功: {admin.username} / {settings.ADMIN_PASSWORD}")
        else:
            print("管理员账号已存在，跳过。")

        # 2. 创建测试读者
        if not db.query(User).filter(User.username == "reader1").first():
            reader = User(
                username="reader1",
                password=hash_password("123456"),
                role="reader",
                real_name="张三",
                phone="13900000001",
                email="reader1@library.com",
            )
            db.add(reader)
            print("测试读者创建成功: reader1 / 123456")

        # 3. 创建预置分类
        categories_data = ["文学", "科技", "历史", "计算机", "艺术"]
        cat_map = {}
        for name in categories_data:
            if not db.query(Category).filter(Category.name == name).first():
                cat = Category(name=name)
                db.add(cat)
                db.flush()
                cat_map[name] = cat.id
                print(f"分类创建成功: {name}")
            else:
                existing = db.query(Category).filter(Category.name == name).first()
                cat_map[name] = existing.id

        # 4. 创建测试图书
        books_data = [
            {
                "title": "红楼梦", "author": "曹雪芹", "isbn": "9787020002207",
                "category_id": cat_map["文学"], "publisher": "人民文学出版社",
                "publish_year": 1996, "total_count": 5, "available_count": 5,
                "summary": "中国古典四大名著之一，描绘了贾宝玉与林黛玉、薛宝钗的爱情故事。",
            },
            {
                "title": "三体", "author": "刘慈欣", "isbn": "9787536692930",
                "category_id": cat_map["科技"], "publisher": "重庆出版社",
                "publish_year": 2008, "total_count": 3, "available_count": 3,
                "summary": "中国科幻文学的里程碑之作，讲述人类文明与三体文明的接触。",
            },
            {
                "title": "明朝那些事儿", "author": "当年明月", "isbn": "9787540461188",
                "category_id": cat_map["历史"], "publisher": "湖南人民出版社",
                "publish_year": 2009, "total_count": 4, "available_count": 4,
                "summary": "以通俗易懂的方式讲述明朝三百年历史。",
            },
            {
                "title": "Python编程：从入门到实践", "author": "Eric Matthes", "isbn": "9787115428028",
                "category_id": cat_map["计算机"], "publisher": "人民邮电出版社",
                "publish_year": 2016, "total_count": 6, "available_count": 6,
                "summary": "Python入门经典教程，适合零基础学习者。",
            },
            {
                "title": "艺术的故事", "author": "贡布里希", "isbn": "9787549550869",
                "category_id": cat_map["艺术"], "publisher": "广西美术出版社",
                "publish_year": 2014, "total_count": 2, "available_count": 2,
                "summary": "西方艺术史的经典入门读物。",
            },
        ]

        for b in books_data:
            if not db.query(Book).filter(Book.isbn == b["isbn"]).first():
                book = Book(**b)
                db.add(book)
                print(f"图书创建成功: {b['title']}")

        # 5. 创建测试借阅记录（含逾期）
        reader = db.query(User).filter(User.username == "reader1").first()
        book1 = db.query(Book).filter(Book.isbn == "9787020002207").first()  # 红楼梦
        book2 = db.query(Book).filter(Book.isbn == "9787536692930").first()  # 三体

        if reader and book1:
            # 正常借阅中
            if not db.query(BorrowRecord).filter(
                BorrowRecord.user_id == reader.id,
                BorrowRecord.book_id == book1.id,
                BorrowRecord.status == "borrowed",
            ).first():
                now = datetime.now()
                record = BorrowRecord(
                    user_id=reader.id,
                    book_id=book1.id,
                    borrow_time=now,
                    due_time=now + timedelta(days=settings.LOAN_PERIOD_DAYS),
                    status="borrowed",
                )
                db.add(record)
                book1.available_count -= 1
                print("测试借阅记录创建成功: 红楼梦（借阅中）")

        if reader and book2:
            # 逾期记录
            if not db.query(BorrowRecord).filter(
                BorrowRecord.user_id == reader.id,
                BorrowRecord.book_id == book2.id,
                BorrowRecord.status == "overdue",
            ).first():
                now = datetime.now()
                borrow_time = now - timedelta(days=40)
                due_time = borrow_time + timedelta(days=settings.LOAN_PERIOD_DAYS)
                record = BorrowRecord(
                    user_id=reader.id,
                    book_id=book2.id,
                    borrow_time=borrow_time,
                    due_time=due_time,
                    status="overdue",
                )
                db.add(record)
                book2.available_count -= 1
                print("测试借阅记录创建成功: 三体（逾期）")

        db.commit()
        print("\n数据库初始化完成！")
        print(f"管理员账号: {settings.ADMIN_USERNAME} / {settings.ADMIN_PASSWORD}")
        print("测试读者: reader1 / 123456")

    except Exception as e:
        db.rollback()
        print(f"初始化失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()

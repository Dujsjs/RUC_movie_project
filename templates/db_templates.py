#@Mengchu Feng---2021201793

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import sys

app = Flask(__name__)

#初始化数据库
WIN = sys.platform.startswith('win')
if WIN: # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else: # 否则使用四个斜线
    prefix = 'sqlite:////'

app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db') #默认将数据库文件放置在本程序实例所在的根目录
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
movie_db = SQLAlchemy(app)

#创建关联表，关联表不存储数据，仅用来存储关系两侧模型的外键对应关系；自动管理，无需手动操作
assoc_table = movie_db.Table('Movie_Actor', 
                             movie_db.Column('movie_id', movie_db.String(10), movie_db.ForeignKey('movie_info.mv_id')),
                             movie_db.Column('act_id', movie_db.String(10), movie_db.ForeignKey('actor_info.act_id')),
                             movie_db.Column('relation_type', movie_db.String(20))
                             ) #这里要和上方创建的类相互对应

#创建模型类
class Movie_info(movie_db.Model):
    mv_id = movie_db.Column(movie_db.String(10), nullable = False, primary_key=True)
    mv_name = movie_db.Column(movie_db.String(20), nullable = False)
    rls_date = movie_db.Column(movie_db.DateTime)
    mv_country = movie_db.Column(movie_db.String(20))
    mv_type = movie_db.Column(movie_db.String(10))
    year = movie_db.Column(movie_db.Integer) #这里要限制输入年份的区间1000~2100，可以在前端限制
    mv_box = movie_db.Column(movie_db.Float)
    mark = movie_db.Column(movie_db.Text) #从网站爬取的评价
    user_mv_comments = movie_db.Column(movie_db.Text) #用户在系统中发表的评价
    mv_awards = movie_db.Column(movie_db.Text) #电影获得的奖项
    actors = movie_db.relationship('Actor_info', secondary = assoc_table, back_populates = 'movies')

class Actor_info(movie_db.Model):
    act_id = movie_db.Column(movie_db.String(10), nullable = False, primary_key=True)
    act_name = movie_db.Column(movie_db.String(20), nullable = False)
    gender = movie_db.Column(movie_db.String(2), nullable = False)
    act_country = movie_db.Column(movie_db.String(20))
    user_actor_comments = movie_db.Column(movie_db.Text)
    actor_awards = movie_db.Column(movie_db.Text)
    movies = movie_db.relationship('Movie_info', secondary = assoc_table, back_populates = 'actors')






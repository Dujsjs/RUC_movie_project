#@Mengchu Feng---2021201793

from flask import Flask, render_template
from flask import request, url_for, redirect, flash
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, DateField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
from datetime import datetime
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
app.secret_key = '123'
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
    online_rate = movie_db.Column(movie_db.Float) #从网站爬取的评分

class Actor_info(movie_db.Model):
    act_id = movie_db.Column(movie_db.String(10), nullable = False, primary_key=True)
    act_name = movie_db.Column(movie_db.String(20), nullable = False)
    gender = movie_db.Column(movie_db.String(2))
    act_country = movie_db.Column(movie_db.String(20))

class User_info(movie_db.Model):
    username = movie_db.Column(movie_db.String(10), nullable = False, primary_key=True)
    tag = movie_db.Column(movie_db.String(40)) #用不多于20个字描述一下自己

class Mv_Act(movie_db.Model):
    relation_type = movie_db.Column(movie_db.String(10), nullable = False, primary_key=True) #只允许填写主演、导演
    act_id = movie_db.Column(movie_db.String(10), nullable = False)
    mv_id = movie_db.Column(movie_db.String(10), nullable = False)
    
class Mv_User():
    mv_rate= movie_db.Column(movie_db.Float, nullable = False, primary_key=True)  #用户在系统中的评分
    username = movie_db.Column(movie_db.String(10), nullable = False)
    mv_id = movie_db.Column(movie_db.String(10), nullable = False)

class Act_User():
    act_rate = movie_db.Column(movie_db.Float, nullable = False, primary_key=True) #用户在系统中的评分
    username = movie_db.Column(movie_db.String(10), nullable = False)
    act_id = movie_db.Column(movie_db.String(10), nullable = False)

#以下为相关装饰器及其对应函数：
@app.route('/', methods = ['GET', 'POST'])
def search():
    if request.method == 'POST': #关键，如果表单提交了再渲染搜索结果的界面！！
        if 'search_mv' in request.form: #一个页面有多份表单时，根据提交的表单进行跳转
            #传入前端表单用户输入的数据
            mv_id = request.form.get('mv_id') 
            mv_name = request.form.get('mv_name') 
            date = request.form.get('date')
            if date:
                date = datetime.strptime(date, "%Y-%m-%d") #时间非空，再进行转化
            mv_country = request.form.get('mv_country')
            mv_type = request.form.get('mv_type')
            box_1 = request.form.get('box_1')
            box_2 = request.form.get('box_2')

            #构建查询，逐步筛选
            temp_query = Movie_info.query
            if mv_id:
                temp_query = temp_query.filter(Movie_info.mv_id == mv_id)
            if mv_name:
                temp_query = temp_query.filter(Movie_info.mv_name.ilike(f'%{mv_name}%'))
            if date:
                temp_query = temp_query.filter(Movie_info.rls_date == date)
            if mv_country:
                temp_query = temp_query.filter(Movie_info.mv_country.ilike(f'%{mv_country}%'))
            if mv_type:
                temp_query = temp_query.filter(Movie_info.mv_type.ilike(f'%{mv_type}%'))
            if box_1 == '选出大于该票房的':
                temp_query = temp_query.filter(Movie_info.mv_box > box_2)
            elif box_1 == '选出小于等于该票房的':
                temp_query = temp_query.filter(Movie_info.mv_box <= box_2)
            else:
                pass
            search_rst = temp_query.all()
            return render_template('search_mv.html', rst_movies = search_rst)
        
        elif 'search_act' in request.form:
            act_id = request.form.get('act_id')
            act_name = request.form.get('act_name')
            gender = request.form.get('gender')
            act_country = request.form.get('act_country')

            temp_query = Movie_info.query
            if act_id:
                temp_query = temp_query.filter(Actor_info.act_id == act_id)
            if act_name:
                temp_query = temp_query.filter(Actor_info.act_name.ilike(f'%{act_name}%'))
            if gender:
                temp_query = temp_query.filter(Actor_info.gender == gender)
            if act_country:
                temp_query = temp_query.filter(Actor_info.act_country.ilike(f'%{act_country}%'))
            search_rst = temp_query.all()
            return render_template('search_act.html', rst_actors = search_rst)
        
        else:
            return redirect(url_for('/')) #收到不知名表单，则跳转回主页
        
    else: #若未填写表单并发出搜索请求，则直接显示电影展示界面
        return render_template('mainpage_base.html')

@app.route('/edit', methods = ['GET', 'POST']) #编辑信息装饰器
def edit():
    return render_template('admin_page.html')


    
#@app.route('/userpage/<string: username>', methods = ['GET', 'POST'])
#def import_data()

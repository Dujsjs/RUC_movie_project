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

# class Movie_form(FlaskForm):  #创建电影表单，并对域完整性进行维护
#     mv_name = StringField('Movie_name', validators = [DataRequired(), Length(min=1, max=20)])
#     rls_date = DateField('Release_date', format = '%Y/%m/%d')
#     mv_country = SelectField('Movie_country', choices = [('中国','中国'),
#                                                         ('法国','法国'),
#                                                         ('日本','日本'),
#                                                         ('澳大利亚','澳大利亚'),
#                                                         ('英国','英国'),
#                                                         ('埃及','埃及'),
#                                                         ('加拿大','加拿大'),
#                                                         ('韩国','韩国'),
#                                                         ('美国','美国'),
#                                                         ('墨西哥','墨西哥'),
#                                                         ('巴西','巴西'),
#                                                         ('巴拿马','巴拿马'),
#                                                         ('波兰','波兰'),
#                                                         ('芬兰','芬兰'),
#                                                         ('瑞典','瑞典'),
#                                                         ('挪威','挪威'),
#                                                         ('菲律宾','菲律宾'),
#                                                         ('越南','越南'),
#                                                         ('老挝','老挝'),
#                                                         ('印度','印度'),
#                                                         ('巴基斯坦','巴基斯坦')])
#     mv_type = SelectField('Movie_type', choices = [('动作','动作'),
#                                                 ('爱情','爱情'),
#                                                 ('喜剧','喜剧'),
#                                                 ('战争','战争'),
#                                                 ('恐怖','恐怖'),
#                                                 ('文艺','文艺'),
#                                                 ('科幻','科幻'),
#                                                 ('伦理','伦理'),
#                                                 ('冒险','冒险'),
#                                                 ('剧情','剧情'),
#                                                 ('惊悚','惊悚'),
#                                                 ('家庭','家庭'),
#                                                 ('运动','运动'),
#                                                 ('奇幻','奇幻'),
#                                                 ('历史','历史'),
#                                                 ('悬疑','悬疑'),
#                                                 ('歌舞','歌舞'),
#                                                 ('纪录','纪录'),
#                                                 ('犯罪','犯罪'),
#                                                 ('西部','西部')])
#     mv_box = FloatField('Movie_box')
#     mark = TextAreaField('Movie_remark') #从网站爬取的评价
#     user_mv_comments = TextAreaField('User_remark') #用户在系统中发表的评价
#     mv_awards = TextAreaField('Movie_awards') #电影获得的奖项
#     movie_search_submit = SubmitField('Search_movie')

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

#@app.route('/search', methods = ['GET', 'POST']) #搜索装饰器



    
#@app.route('/userpage/<string: username>', methods = ['GET', 'POST'])
#def import_data()

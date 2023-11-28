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
import click

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

#创建模型类
class Movie_info(movie_db.Model):
    mv_id = movie_db.Column(movie_db.String(10), nullable = False, primary_key=True)
    mv_name = movie_db.Column(movie_db.String(20), nullable = False)
    rls_date = movie_db.Column(movie_db.String(20))
    mv_country = movie_db.Column(movie_db.String(20))
    mv_type = movie_db.Column(movie_db.String(10))
    year = movie_db.Column(movie_db.String(10)) #这里要限制输入年份的区间1000~2100，可以在前端限制
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
    id = movie_db.Column(movie_db.String(10), nullable = False, primary_key=True)
    relation_type = movie_db.Column(movie_db.String(10), nullable = False) #只允许填写主演、导演
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
@app.cli.command('drill_data')
def drill_data():
    movie_db.create_all() #首先生成数据文件，此处的格式化数据使用T-SQL输出（见SQL文件）
    act_info = [
        {'act_id':'2001', 'act_name':'吴京', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2002', 'act_name':'饺子', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2003', 'act_name':'屈楚萧', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2004', 'act_name':'郭帆', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2005', 'act_name':'乔罗素', 'gender':'男', 'act_country':'美国'}, 
        {'act_id':'2006', 'act_name':'小罗伯特·唐尼', 'gender':'男', 'act_country':'美国'}, 
        {'act_id':'2007', 'act_name':'克里斯·埃文斯', 'gender':'男', 'act_country':'美国'}, 
        {'act_id':'2008', 'act_name':'林超贤', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2009', 'act_name':'张译', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2010', 'act_name':'黄景瑜', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2011', 'act_name':'陈思诚', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2012', 'act_name':'王宝强', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2013', 'act_name':'刘昊然', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2014', 'act_name':'文牧野', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2015', 'act_name':'徐峥', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2016', 'act_name':'刘伟强', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2017', 'act_name':'张涵予', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2018', 'act_name':'F·加里·格雷', 'gender':'男', 'act_country':'美国'}, 
        {'act_id':'2019', 'act_name':'范·迪塞尔', 'gender':'男', 'act_country':'美国'}, 
        {'act_id':'2020', 'act_name':'杰森·斯坦森', 'gender':'男', 'act_country':'美国'}, 
        {'act_id':'2021', 'act_name':'闫非', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2022', 'act_name':'沈腾', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2023', 'act_name':'安东尼·罗素', 'gender':'男', 'act_country':'美国'}, 
        {'act_id':'2024', 'act_name':'克里斯·海姆斯沃斯', 'gender':'男', 'act_country':'美国'}, 
        {'act_id':'2025', 'act_name':'许诚毅', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2026', 'act_name':'梁朝伟', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2027', 'act_name':'白百何', 'gender':'女  ', 'act_country':'中国'}, 
        {'act_id':'2028', 'act_name':'井柏然', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2029', 'act_name':'管虎', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2030', 'act_name':'王千源', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2031', 'act_name':'姜武', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2032', 'act_name':'宁浩', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2033', 'act_name':'葛优', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2034', 'act_name':'范伟', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2035', 'act_name':'贾玲', 'gender':'女  ', 'act_country':'中国'}, 
        {'act_id':'2036', 'act_name':'张小斐', 'gender':'女  ', 'act_country':'中国'}, 
        {'act_id':'2037', 'act_name':'陈凯歌', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2038', 'act_name':'徐克', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2039', 'act_name':'易烊千玺', 'gender':'男', 'act_country':'中国'}, 
        {'act_id':'2040', 'act_name':'林诣彬', 'gender':'男', 'act_country':'美国'}, 
        {'act_id':'2041', 'act_name':'米歇尔·罗德里格兹', 'gender':'女', 'act_country':'美国'}
    ]
    mv_info = [
        {'mv_id':'1001', 'mv_name':'战狼2', 'rls_date':'07 27 2017 12:00AM', 'mv_country':'中国', 'type':'战争', 'year':'2017', 'box':'56.84'},
        {'mv_id':'1002', 'mv_name':'哪吒之魔童降世', 'rls_date':'07 26 2019 12:00AM', 'mv_country':'中国', 'type':'动画', 'year':'2019', 'box':'50.15'},
        {'mv_id':'1003', 'mv_name':'流浪地球', 'rls_date':'02  5 2019 12:00AM', 'mv_country':'中国', 'type':'科幻', 'year':'2019', 'box':'46.86'},
        {'mv_id':'1004', 'mv_name':'复仇者联盟4', 'rls_date':'04 24 2019 12:00AM', 'mv_country':'美国', 'type':'科幻', 'year':'2019', 'box':'42.5'},
        {'mv_id':'1005', 'mv_name':'红海行动', 'rls_date':'02 16 2018 12:00AM', 'mv_country':'中国', 'type':'战争', 'year':'2018', 'box':'36.5'},
        {'mv_id':'1006', 'mv_name':'唐人街探案2', 'rls_date':'02 16 2018 12:00AM', 'mv_country':'中国', 'type':'喜剧', 'year':'2018', 'box':'33.97'},
        {'mv_id':'1007', 'mv_name':'我不是药神', 'rls_date':'07  5 2018 12:00AM', 'mv_country':'中国', 'type':'喜剧', 'year':'2018', 'box':'31'},
        {'mv_id':'1008', 'mv_name':'中国机长', 'rls_date':'09 30 2019 12:00AM', 'mv_country':'中国', 'type':'剧情', 'year':'2019', 'box':'29.12'},
        {'mv_id':'1009', 'mv_name':'速度与激情8', 'rls_date':'04 14 2017 12:00AM', 'mv_country':'美国', 'type':'动作', 'year':'2017', 'box':'26.7'},
        {'mv_id':'1010', 'mv_name':'西虹市首富', 'rls_date':'07 27 2018 12:00AM', 'mv_country':'中国', 'type':'喜剧', 'year':'2018', 'box':'25.47'},
        {'mv_id':'1011', 'mv_name':'复仇者联盟3', 'rls_date':'05 11 2018 12:00AM', 'mv_country':'美国', 'type':'科幻', 'year':'2018', 'box':'23.9'},
        {'mv_id':'1012', 'mv_name':'捉妖记2', 'rls_date':'02 16 2018 12:00AM', 'mv_country':'中国', 'type':'喜剧', 'year':'2018', 'box':'22.37'},
        {'mv_id':'1013', 'mv_name':'八佰', 'rls_date':'08 21 2020 12:00AM', 'mv_country':'中国', 'type':'战争', 'year':'2020', 'box':'30.1'},
        {'mv_id':'1014', 'mv_name':'姜子牙', 'rls_date':'10  1 2020 12:00AM', 'mv_country':'中国', 'type':'动画', 'year':'2020', 'box':'16.02'},
        {'mv_id':'1015', 'mv_name':'我和我的家乡', 'rls_date':'10  1 2020 12:00AM', 'mv_country':'中国', 'type':'剧情', 'year':'2020', 'box':'28.29'},
        {'mv_id':'1016', 'mv_name':'你好，李焕英', 'rls_date':'02 12 2021 12:00AM', 'mv_country':'中国', 'type':'喜剧', 'year':'2021', 'box':'54.13'},
        {'mv_id':'1017', 'mv_name':'长津湖', 'rls_date':'09 30 2021 12:00AM', 'mv_country':'中国', 'type':'战争', 'year':'2021', 'box':'53.48'},
        {'mv_id':'1018', 'mv_name':'速度与激情9', 'rls_date':'05 21 2021 12:00AM', 'mv_country':'中国', 'type':'动作', 'year':'2021', 'box':'13.92'}
    ]
    mv_act_relation = [
        {'id':'1', 'mv_id':'1001', 'act_id':'2001', 'relation_type':'主演'},
        {'id':'10', 'mv_id':'1005', 'act_id':'2008', 'relation_type':'导演'},
        {'id':'11', 'mv_id':'1005', 'act_id':'2009', 'relation_type':'主演'},
        {'id':'12', 'mv_id':'1005', 'act_id':'2010', 'relation_type':'主演'},
        {'id':'13', 'mv_id':'1006', 'act_id':'2011', 'relation_type':'导演'},
        {'id':'14', 'mv_id':'1006', 'act_id':'2012', 'relation_type':'主演'},
        {'id':'15', 'mv_id':'1006', 'act_id':'2013', 'relation_type':'主演'},
        {'id':'16', 'mv_id':'1007', 'act_id':'2014', 'relation_type':'导演'},
        {'id':'17', 'mv_id':'1007', 'act_id':'2015', 'relation_type':'主演'},
        {'id':'18', 'mv_id':'1008', 'act_id':'2016', 'relation_type':'导演'},
        {'id':'19', 'mv_id':'1008', 'act_id':'2017', 'relation_type':'主演'},
        {'id':'2', 'mv_id':'1001', 'act_id':'2001', 'relation_type':'导演'},
        {'id':'20', 'mv_id':'1009', 'act_id':'2018', 'relation_type':'导演'},
        {'id':'21', 'mv_id':'1009', 'act_id':'2019', 'relation_type':'主演'},
        {'id':'22', 'mv_id':'1009', 'act_id':'2020', 'relation_type':'主演'},
        {'id':'23', 'mv_id':'1010', 'act_id':'2021', 'relation_type':'导演'},
        {'id':'24', 'mv_id':'1010', 'act_id':'2022', 'relation_type':'主演'},
        {'id':'25', 'mv_id':'1011', 'act_id':'2023', 'relation_type':'导演'},
        {'id':'26', 'mv_id':'1011', 'act_id':'2006', 'relation_type':'主演'},
        {'id':'27', 'mv_id':'1011', 'act_id':'2024', 'relation_type':'主演'},
        {'id':'28', 'mv_id':'1012', 'act_id':'2025', 'relation_type':'导演'},
        {'id':'29', 'mv_id':'1012', 'act_id':'2026', 'relation_type':'主演'},
        {'id':'3', 'mv_id':'1002', 'act_id':'2002', 'relation_type':'导演'},
        {'id':'30', 'mv_id':'1012', 'act_id':'2027', 'relation_type':'主演'},
        {'id':'31', 'mv_id':'1012', 'act_id':'2028', 'relation_type':'主演'},
        {'id':'32', 'mv_id':'1013', 'act_id':'2029', 'relation_type':'导演'},
        {'id':'33', 'mv_id':'1013', 'act_id':'2030', 'relation_type':'主演'},
        {'id':'34', 'mv_id':'1013', 'act_id':'2009', 'relation_type':'主演'},
        {'id':'35', 'mv_id':'1013', 'act_id':'2031', 'relation_type':'主演'},
        {'id':'36', 'mv_id':'1015', 'act_id':'2032', 'relation_type':'导演'},
        {'id':'37', 'mv_id':'1015', 'act_id':'2015', 'relation_type':'导演'},
        {'id':'38', 'mv_id':'1015', 'act_id':'2011', 'relation_type':'导演'},
        {'id':'39', 'mv_id':'1015', 'act_id':'2015', 'relation_type':'主演'},
        {'id':'4', 'mv_id':'1003', 'act_id':'2001', 'relation_type':'主演'},
        {'id':'40', 'mv_id':'1015', 'act_id':'2033', 'relation_type':'主演'},
        {'id':'41', 'mv_id':'1015', 'act_id':'2034', 'relation_type':'主演'},
        {'id':'42', 'mv_id':'1016', 'act_id':'2035', 'relation_type':'导演'},
        {'id':'43', 'mv_id':'1016', 'act_id':'2035', 'relation_type':'主演'},
        {'id':'44', 'mv_id':'1016', 'act_id':'2036', 'relation_type':'主演'},
        {'id':'45', 'mv_id':'1016', 'act_id':'2022', 'relation_type':'主演'},
        {'id':'46', 'mv_id':'1017', 'act_id':'2037', 'relation_type':'导演'},
        {'id':'47', 'mv_id':'1017', 'act_id':'2038', 'relation_type':'导演'},
        {'id':'48', 'mv_id':'1017', 'act_id':'2008', 'relation_type':'导演'},
        {'id':'49', 'mv_id':'1017', 'act_id':'2001', 'relation_type':'主演'},
        {'id':'5', 'mv_id':'1003', 'act_id':'2003', 'relation_type':'主演'},
        {'id':'50', 'mv_id':'1017', 'act_id':'2039', 'relation_type':'主演'},
        {'id':'51', 'mv_id':'1018', 'act_id':'2040', 'relation_type':'导演'},
        {'id':'52', 'mv_id':'1018', 'act_id':'2019', 'relation_type':'主演'},
        {'id':'53', 'mv_id':'1018', 'act_id':'2041', 'relation_type':'主演'},
        {'id':'6', 'mv_id':'1003', 'act_id':'2004', 'relation_type':'导演'},
        {'id':'7', 'mv_id':'1004', 'act_id':'2005', 'relation_type':'导演'},
        {'id':'8', 'mv_id':'1004', 'act_id':'2006', 'relation_type':'主演'},
        {'id':'9', 'mv_id':'1004', 'act_id':'2007', 'relation_type':'主演'}
    ]

    for a in act_info:
        temp_act = Actor_info(act_id = a['act_id'], act_name = a['act_name'], gender = a['gender'], act_country = a['act_country'])
        movie_db.session.add(temp_act)
    for m in mv_info:
        temp_mv = Movie_info(mv_id = m['mv_id'], mv_name = m['mv_name'], rls_date = m['rls_date'], mv_country = m['mv_country'], mv_type = m['type'], year = m['year'], mv_box = m['box'])
        movie_db.session.add(temp_mv)
    for r in mv_act_relation:
        temp_relation = Mv_Act(id = r['id'], relation_type = r['relation_type'], act_id = r['act_id'], mv_id = r['mv_id'])
        movie_db.session.add(temp_relation)

    movie_db.session.commit()
    click.echo('初始化电影数据已经导入！')

@app.route('/', methods = ['GET', 'POST'])
def search():
    if request.method == 'POST': #关键，如果表单提交了再渲染搜索结果的界面！！
        if 'search_mv' in request.form: #一个页面有多份表单时，根据提交的表单进行跳转
            #传入前端表单用户输入的数据
            mv_id = request.form.get('mv_id') 
            mv_name = request.form.get('mv_name') 
            date = request.form.get('date')
            if date:
                date = datetime.strptime(date, "%m-%d-%Y") #时间非空，再进行转化
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

            temp_query = Actor_info.query
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

@app.route('/admin', methods = ['GET', 'POST']) #编辑信息装饰器
def demo():
    if request.method == 'GET':
        search_rst = Movie_info.query.all() #未提交表单，则仅仅渲染页面
        return render_template('admin_page.html', rst_movies = search_rst)
    if request.method == 'POST':
        search_rst = Movie_info.query.all() #提交了表单，首先保证仍然显示所有电影信息
        
        new_data = request.get_json() #以嵌套字典的形式返回输入值

        temp_mv_info = Movie_info(mv_id = new_data['form1']['mv_id'], mv_name = new_data['form1']['mv_name'], rls_date = new_data['form1']['date'], mv_country = new_data['form1']['mv_country'], mv_type = new_data['form1']['mv_type'], year = (new_data['form1']['date'])[-4:], mv_box = new_data['form1']['box']) #更新电影表信息
        movie_db.session.add(temp_mv_info)

        all_act_form = list(new_data.keys())
        del all_act_form[0]
        for form_name in all_act_form:
            temp_act_info = Actor_info(act_id = new_data[form_name]['act_id'], act_name = new_data[form_name]['act_name'], gender = new_data[form_name]['gender'], act_country = new_data[form_name]['country']) #更新演员表信息
            id_list = Mv_Act.query.with_entities(Mv_Act.id).all() #查找当前的id编号
            max_id_current = max(list(map(int, id_list))) #找出最大值，加1即可实现自动编号
            temp_act_mv_relation = Mv_Act(id = str(max_id_current + 1), relation_type = new_data[form_name]['act_relation'], act_id = new_data[form_name]['act_id'], mv_id = new_data['form1']['mv_id']) #更新关系表信息
            movie_db.session.add(temp_act_info)
            movie_db.session.add(temp_act_mv_relation)

        movie_db.session.commit() #最终全部提交
        return render_template('admin_page.html', rst_movies = search_rst)

    
#@app.route('/userpage/<string: username>', methods = ['GET', 'POST'])
#def import_data()

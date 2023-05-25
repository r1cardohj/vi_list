import unittest

from vi_list import app,db
from vi_list.models import  Movie,User
from vi_list.commands import forge,initdb

class MovieListTESTCase(unittest.TestCase):
    
    # 更新配置
    def setUp(self):
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'
        )
        # 创建数据库和表
        db.create_all()
        # 创建测试数据，一个用户，一个电影条目
        user = User(name='Test', username='test')
        user.set_password('123')
        movie = Movie(title='test movie', year='2012')
        # 使用 add_all() 方法一次添加多个模型类实例，传入列表
        db.session.add_all([user, movie])
        db.session.commit()

        self.client = app.test_client()  # 创建测试客户端
        self.runner = app.test_cli_runner()  # 创建测试命令运行器

    
    
    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        
    
    def test_app_exist(self):
        self.assertIsNotNone(app)
    
    
    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])
        
   
    def test_404_page(self):
        response =self.client.get('/nothing')
        data = response.get_data(as_text = True)
        self.assertIn('404', data)
        self.assertIn('返回首页', data)
        self.assertEqual(response.status_code, 404)
    
    
    def test_index_page(self):
        """测试主页
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code,200)
    
    
    def login(self):
        self.client.post('/login', data=dict(
            username='test',
            pw='123'
        ), follow_redirects=True)
    
    
    def test_add_movie(self):
        self.login() #登录
        response = self.client.post('/add',data=dict(
            title = "test movie1",
            year = '2023'
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('success',data)
        self.assertIn('test movie1')
    
        #电影标题为空
        response = self.client.post('/add', data=dict(
            title='',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('success', data)
        self.assertIn('非法输入', data)
        
        #年份为空
        response = self.client.post('/add', data=dict(
            title='New Movie',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('success', data)
        self.assertIn('非法输入', data)
    
    
    def test_update_movie(self):
        self.login() #登录
        # 测试更新页面
        response = self.client.get('/movie/edit/1')
        data = response.get_data(as_text=True)
        self.assertIn('Edit item', data)
        self.assertIn('test movie', data)
        self.assertIn('2012', data)

        # 测试更新条目操作
        response = self.client.post('/movie/edit/1', data=dict(
            title='New Movie Edited',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('updated succeefully!', data)
        self.assertIn('New Movie Edited', data)

        # 测试更新条目操作，但电影标题为空
        response = self.client.post('/movie/edit/1', data=dict(
            title='',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('updated succeefully!', data)
        self.assertIn('非法输入', data)

        # 测试更新条目操作，但电影年份为空
        response = self.client.post('/movie/edit/1', data=dict(
            title='New Movie Edited Again',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('updated succeefully!', data)
        self.assertNotIn('New Movie Edited Again', data)
        #self.assertIn('Invalid input.', data)
        
        def test_delete_item(self):
            self.login()

        response = self.client.post('/movie/delete/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('del successfully!', data)
        self.assertNotIn('test movie', data)
    
    
    def test_index_nologin(self):
        """测试未登录首页
        """
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertNotIn('Logout',data)
        self.assertNotIn('setting',data)
        self.assertNotIn('Add',data)
        self.assertNotIn('delete',data)
        self.assertNotIn('Edit',data)
    
    
    def test_login(self):
        """测试登录
        """
        response = self.client.post('/login',data=dict(
            username = 'test',
            pw = '123'
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Login success.',data)
        self.assertNot('Logout',data)
        self.assertNot('setting',data)
        self.assertNot('Add',data)
        self.assertNot('delete',data)
        self.assertNot('Edit',data)
        
        # 测试使用错误的密码登录
        response = self.client.post('/login', data=dict(
            username='test',
            password='456'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('are you kiding me?', data)

        # 测试使用错误的用户名登录
        response = self.client.post('/login', data=dict(
            username='wrong',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('are you kiding me?', data)
        
        # 测试使用错误的用户名登录
        response = self.client.post('/login', data=dict(
            username='wrong',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('are you kiding me?', data)

        # 测试使用空用户名登录
        response = self.client.post('/login', data=dict(
            username='',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('are you kiding me?', data)

        # 测试使用空密码登录
        response = self.client.post('/login', data=dict(
            username='test',
            password=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('are you kiding me?', data)

    
    # 测试登出
    def test_logout(self):
        self.login()

        response = self.client.get('/logout', follow_redirects=True)
        data = response.get_data(as_text=True)
        #self.assertIn('Goodbye.', data)
        self.assertNotIn('Logout', data)
        self.assertNotIn('setting', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('Edit', data)
    
    
    def test_settings(self):
        self.login()

        # 测试设置页面
        response = self.client.get('/setting')
        data = response.get_data(as_text=True)
        self.assertIn('setting', data)
        #self.assertIn('Your Name', data)

        # 测试更新设置
        response = self.client.post('/setting', data=dict(
            name='hj',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('setting successfully!', data)
        self.assertIn('hj', data)

        # 测试更新设置，名称为空
        response = self.client.post('/setting', data=dict(
            name='',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Settings updated.', data)
        self.assertIn('非法输入', data)
    
    
    def test_forge_command(self):
        """测试flask forge 命令
        """
        result = self.runner.invoke(forge)
        self.assertIn('Done',result.output)
        self.assertNotEqual(Movie.query.count(),0)
    
    def test_initdb_command(self):
        result = self.runner.invoke(initdb)
        self.assertIn('Initialized database.', result.output)
    
    
    # 测试生成管理员账户
    def test_admin_command(self):
        db.drop_all()
        db.create_all()
        result = self.runner.invoke(args=['admin', '--username', 'admin', '--pw', '123'])
        self.assertIn('Create user...', result.output)
        self.assertIn('Done', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'admin')
        self.assertTrue(User.query.first().validate_password('123'))

if __name__ == '__main__':
    unittest.main()
import threading
import mimetypes,json
import requests
import re,os,time,pymysql

class wordpress_post:
    def __init__(self,tittle,content):
        self.tittle=tittle
        self.content=content
    def mysql_con(self):
        conn = pymysql.connect(host='数据库地址', port=3306, user='root', passwd='数据库密码', db='wordpress', charset='utf8') #数据库填这里
        return conn
    def up(self):
        times=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        sql="INSERT INTO wp_posts(post_author,post_date,post_content,post_title,post_excerpt,post_status,comment_status,ping_status,post_name,to_ping,pinged,post_modified,post_content_filtered,post_parent,menu_order,post_type,comment_count) VALUES ('1','%s','%s','%s','','publish','open','open','%s','','','%s','','0','0','post','0')" % (str(times),str(self.content),str(self.tittle),str(self.tittle),str(times))
        return sql
    def cat(self,ids,cat):
        sql="INSERT INTO wp_term_relationships(object_id,term_taxonomy_id,term_order) VALUES (%s,%s,'0')"%(ids,cat)
        return sql
    def close_mysql(self,cursor,conn):
        conn.commit()
        cursor.close()
        conn.close()
#上传图床
def upload(files):
    APIKey = "987893b2fdfasfasdfsafsa" #API填这里
    format = "json"
    url = "https://图床地址/api/1/upload/?key="+ APIKey + "&source="+ files +"&format=" + format #图床地址
    try:
        r = requests.post(url)
    except:
        print("图床超时")
        return json.loads()
    return json.loads(r.text)
#上传WordPress
def post_article(tittle):
    with open('temp/temp.txt','r') as f:
        wz_content=f.read()
    with open('temp/tj.txt','r') as f:
        wzs=f.read()
    k=int(wzs)
    a=wordpress_post(str(tittle[0]),wz_content)
    conn=a.mysql_con()
    cursor = conn.cursor()
    c=a.up()
    effect_row = cursor.execute(c)
    new_id = cursor.lastrowid
    d=a.cat(new_id,'1') #文章分类，去wp_term_taxonomy里找你需要的id
    effect_row = cursor.execute(d)
    a.close_mysql(cursor,conn)
    print('文章已发布:'+tittle[0])
    os.remove('temp/temp.txt')
    k+=1
    j=str(k)
    with open('temp/tj.txt','w+') as f:
        f.write(j)
def main():
    flag=1
    while flag<=270:
        base_url='https://t66y.com/'
        page_url='https://t66y.com/thread0806.php?fid=8&search=&page='+str(flag)
        get=requests.get(page_url)
        article_url=re.findall(r'<h3><a href="(.*)" target="_blank" id="">(?!<.*>).*</a></h3>',str(get.content,'gbk',errors='ignore'))
        for url in article_url:
            tittle=['default']
            getpage=requests.get(str(base_url)+str(url))
            tittle=re.findall(r'<h4>(.*)</h4>',str(getpage.content,'gbk',errors='ignore'))
            img_url=re.findall(r'<input data-src=\'(.*?)\'',str(getpage.content,'gbk',errors='ignore'))
            if img_url == []:
                img_url=re.findall(r'<input data-link=\'(.*?)\'',str(getpage.content,'gbk',errors='ignore'))           
            print('开始上传图片')
            for download_url in img_url:
                try:
                    b = upload(download_url)
                except:
                    continue
                img_hc='<img src="'+b['image']['url']+'">'
                with open('temp/temp.txt','a+') as f:
                    f.write(img_hc)
                print("完成上传1张")
            #上传文章            
            post_article(tittle)
            time.sleep(30)
        print('第'+str(flag)+'页下载完成')
        flag=flag+1
        
if __name__=='__main__':
    try:
        if os.path.exists('temp')==False:
            os.makedirs('temp')
            f=open('temp/tj.txt','w+')
            f.close()
            with open('temp/tj.txt','w+') as f:
                f.write('0')
            main()
        else:
            main()
    except:
        print('主程序出错，请重新运行')
        
#tj.txt里记录了采集了多少篇，可以用来更新wp_term_taxonomy中对应项的count值（如果这个分类里只有采集的话）
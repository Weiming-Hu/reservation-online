# 在新浪云上部署Django应用程序


[TOC]



###前言###

近日，笔者利用空闲时间写了一个简单的在线预约系统，使用的工具包括Python 3.5.1 和 Django 1.9.5 。早就有听说Django响亮的口号，“The web framework for perfectionists with deadlines”。这次自己亲自尝试了过后，发现果然名不虚传，清晰简洁的支持文档，方便的API接口，都无一例外的吸引了我。

既然是一个在线系统，那么肯定绕不开服务器部署的问题。我选择了方便的新浪云作为后端服务器。原本以为会比较顺利，没想到里面细节设置还是比较多的。在这里，笔者记录下这些细节设置，也算是一个比较基础的**新浪云入门设置教程**了吧！

- - -

###准备工作###

首先，保证你的系统在本地(127.0.0.1:[default port | 8000])测试无误。

关于笔者的系统的一些基本信息：
1. 后端：Python 3.5.1
2. 框架：Django 1.9.5
3. 数据库：SQLite

在部署之前我曾经担心过，新浪云支不支持Python 3.5呢？支不支持Django 1.9？好像新浪云的云应用手册上面写了仅支持Python 2.7，那是不是意味着无法部署呢？其实并**不是这样的**，我们使用的是新浪云的容器(container)的功能，相当于是一个存放区域，可以存放任何形式的应用程序。这一点后面会讲到。

确认了你的系统信息之后，就要开始准备一些配置文件了，我们需要准备以下文件：
1. runtime.txt
2. requirements.txt
3. Procfile
    （请保证命名一致）

官方参考文档: [Python应用部署](www.sinacloud.com/doc/sae/docker/python-getting-started.html#gou-jian-he-yun-xing-shuo-ming)

##### runtime.txt #####

如果你想要指定你想要使用的Python版本，你可以通过在你的应用的根目录下创建一个 runtime.txt 文件，在里面写上你要使用的Python版本。内容格式如下：

`python-3.5.1`

##### requirements.txt #####

容器云在构建应用的时候自动执行特定的命令来安装所有的第三方依赖包，所以你需要在 requirements.txt 文件中指定你有哪些依赖。内容格式如下：

`django==1.9.5`

这个有个小问题，如果我有若干个第三方依赖库，应该如何定义？行尾需不需要分号？这个语法在文档里没有说明，笔者也没有尝试。如果有了解的请留言，谢谢！

##### Procfile #####

官方参考文档: [Procfile](http://www.sinacloud.com/doc/sae/docker/intro.html#procfile)

这个文件将告诉云端服务器，如何运行你的系统。内容格式如下：

`web: python manage.py runserver 0.0.0.0:5050`

**注意**：Django服务器默认监听的端口是127.0.0.1:8000，这会导致新浪云应用程序的运行实例收不到任何请求，所以，在云端开启服务器的时候，你必须显式地告诉服务器，监听在0.0.0.0这个接口上，默认端口设置为5050。这一点很关键！

最后，我们会用到git命令行进行代码的上传，请确保你的机器上安装有[git命令行工具](https://git-scm.com/download)。

- - -

###开始部署###

首先，在本地运行你的Python服务器。可能是因为之后在上传代码和配置云端，服务器生成镜像的时候，远程服务器和本地服务器需要有链接。如果不在本地启动，会提示错误，生成镜像失败。开启一个终端，进入应用程序根目录，然后执行：

`python manage.py runserver 0.0.0.0:5050`

然后，开启另一个终端，进入应用根程序目录，依次执行以下代码：

```
git remote add sae https://git.sinacloud.com/pailian
git add .
git commit -am "make it better"
git push sae master:1
```

这样之后，我们就已经
1. 创建了一个远程仓库，以后的每一次push都会自动的存放到这个仓库中；
2. 检测了代码是否发生变化；
3. 开始上传代码；

不出意外的话，这个时候需要你输入 == 安全邮箱 == 和 == 安全密码 == 了，不要输错了。

- - -

### 部署成功 ###

上传成功之后，稍等片刻，你就可以登录你的新浪云管理账号，前往 == 应用 == - == 容器管理 == 中，查看 == 状态 == 了。理论上来说应该是“运行”字样。

这里有一个小插曲，在走通了之前的所有步骤，并且没有报错的情况，我等待了超过1小时，发现自己的两个实例的 == 状态 == 依旧是“处理中”。这很是奇怪。没辙了，只能够提交工单，联系客服。后来才知道，原来正好那段时间他们在做系统升级。所以，有的时候，该调戏客服的时候，还是要大胆行动的。

** Weiming **
** 2016.4.21 **
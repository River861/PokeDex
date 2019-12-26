import matplotlib.pyplot as plt
from pylab import *         #支持中文
plt.rcParams['font.family'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False
 
xhl = [0.392, 0.509, 0.447, 0.553, 0.553, 0.674, 0.762, 0.832, 0.832, 0.832, 0.95, 0.886, 0.913, 0.934, 0.95]
x_xhl = range(1, len(xhl) + 1)
xhm = [0.392, 0.509, 0.532, 0.622, 0.622, 0.724, 0.798, 0.857, 0.749, 0.749, -0.122, 0.134]
x_xhm = range(1, len(xhm) + 1)
mcj = [0.392, 0.548, 0.491, 0.589, 0.589, 0.7, 0.781, 0.845, 0.845, 0.255]
x_mcj = range(1, len(mcj) + 1)
klkl = [0.392, 0.548, 0.548, 0.635, 0.635, 0.734, 0.806, 0.38, 0.38]
x_klkl = range(1, len(klkl) + 1)
plt.plot(x_xhl, xhl, label='小火龙')
plt.plot(x_xhm, xhm, label='小火马')
plt.plot(x_mcj, mcj, label='迷唇姐')
plt.plot(x_klkl, klkl, label='卡拉卡拉')
plt.legend() # 让图例生效
plt.xlabel(u"轮数") #X轴标签
plt.ylabel("确信度") #Y轴标签
plt.title("确信度变化轨迹图") #标题
 
plt.show()
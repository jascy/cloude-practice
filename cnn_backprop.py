"""
╔══════════════════════════════════════════════════════════════╗
║  CNN 反向传播 — 纯 NumPy 手写实现                           ║
║                                                              ║
║  包含层: Conv → ReLU → MaxPool/AvgPool → Flatten → FC       ║
║  损失函数: Softmax + 交叉熵 (合并反向)                       ║
║  验证方法: 数值梯度检查 + 训练 loss 监控                     ║
║                                                              ║
║  核心学习目标:                                               ║
║  • 卷积层的反向传播: dW 和 dX 分别怎么算?                    ║
║  • 池化层的梯度如何反向传递? (argmax vs 均匀分配)             ║
║  • Softmax+CrossEntropy 合并反向的经典结论                    ║
║  • 数值梯度验证: 你的反向传播算对了吗?                       ║
╚══════════════════════════════════════════════════════════════╝
"""
import numpy as np


# ============================================================
# 1. 卷积层 (Conv)
# ============================================================
class Conv:
    """
    ╔══════════════════════════════════════════════════════╗
    ║  卷积层: stride=1, padding=0 (valid 卷积)          ║
    ║                                                      ║
    ║  前向传播:                                           ║
    ║    Y[n, i, j, f] = Σ X[patch] ⊙ W[:,:,:,f] + b[f]  ║
    ║    形象理解: W 是"特征检测器"，在输入上滑动扫描      ║
    ║                                                      ║
    ║  反向传播 (两个任务):                                  ║
    ║    dW = X 与 dOut 做 valid 卷积                      ║
    ║         (X 作输入，dOut 作卷积核)                     ║
    ║    dX = dOut 与 W_rot180 做 full 卷积 (转置卷积)      ║
    ║         (把 W 翻转180°后，与 dOut 做全卷积)           ║
    ╚══════════════════════════════════════════════════════╝
    """

    def __init__(self, in_channels, out_channels, kernel_size):
        """
        参数:
            in_channels:  输入通道数 (如 RGB 图像 = 3)
            out_channels: 输出通道数 = 卷积核数量 (滤波器数量)
            kernel_size:  卷积核大小 (3 表示 3×3)
        """
        self.C_in = in_channels        # 输入通道数
        self.F = out_channels          # 滤波器个数 = 输出通道数
        self.K = kernel_size           # 卷积核尺寸 (K×K)

        # ─── He 初始化 ───
        # 为什么用 He 初始化?
        #   ReLU 会让一半神经元"死亡"，所以方差需要放大 2 倍
        #   scale = sqrt(2 / fan_in)
        #   fan_in = in_channels * K * K  (每个滤波器的参数个数)
        scale = np.sqrt(2.0 / (in_channels * kernel_size * kernel_size))
        # 权重形状: (K, K, C_in, F)
        #   解释: 每个输出通道 f 对应一个 (K,K,C_in) 的 3D 滤波器
        self.W = np.random.randn(kernel_size, kernel_size, in_channels, out_channels) * scale
        # 偏置: 每个输出通道一个
        self.b = np.zeros(out_channels)

        # 缓存前向数据，反向时需要用到 X
        self.X = None

    def forward(self, X):
        """
        前向传播: 对输入 X 进行卷积

        输入:
            X: shape = (N, H, W, C_in)
               N  = batch 大小
               H  = 输入高度
               W  = 输入宽度
               C_in = 输入通道数

        输出:
            Y: shape = (N, H_out, W_out, F)
               H_out = H - K + 1  (valid 卷积，不补零)
               W_out = W - K + 1
               F     = out_channels

        直观理解:
            想象一个 3×3 的窗口在图上从左到右、从上到下滑动，
            每次窗口停在一个位置，就把窗口内的像素值 × 滤波器权重，再求和。
            每个滤波器输出一个 feature map（特征图），代表"检测到了什么模式"。
        """
        self.X = X                               # 缓存，反向时需要
        N, H, W, _ = X.shape
        # valid 卷积输出尺寸: 输入 - 核 + 1
        H_out = H - self.K + 1
        W_out = W - self.K + 1

        # 初始化输出张量
        Y = np.zeros((N, H_out, W_out, self.F))

        # ─── 四重循环实现卷积 ───
        # 这是最朴素、最直观的卷积实现（不追求速度，追求可读性）
        for n in range(N):              # 遍历每张图
            for f in range(self.F):     # 遍历每个滤波器
                for i in range(H_out):  # 遍历高度
                    for j in range(W_out):  # 遍历宽度
                        # 从输入中取一个 K×K×C_in 的 patch
                        patch = X[n, i:i + self.K, j:j + self.K, :]
                        # patch ⊙ W[:,:,:,f] 逐元素乘，然后求和
                        Y[n, i, j, f] = np.sum(patch * self.W[:, :, :, f]) + self.b[f]
        return Y

    def backward(self, dOut, lr=0.01):
        """
        卷积层的反向传播 —— 这是整个 CNN 最难的部分

        输入:
            dOut: shape = (N, H_out, W_out, F)
                  上游传来的梯度 ∂L/∂Y
            lr:   学习率 (用于更新参数)

        核心推导 (链式法则):

        [1] 求 dW (损失对权重的梯度)
            由于 Y[n,i,j,f] = Σ patch ⊙ W[:,:,:,f] + b[f]
            对 W[p,q,c,f] 求偏导:
              每个输出位置 (i,j) 都用了 W[p,q,c,f]
              贡献 = dOut[n,i,j,f] × X[n,i+p,i+q,c]
            求和 → dW[p,q,c,f] = Σ_n,i,j dOut[n,i,j,f] × X[n,i+p,i+q,c]
            这就是: X 和 dOut 做 valid 卷积!

        [2] 求 dX (损失对输入的梯度，传给上一层)
            X 的一个元素影响了所有用到它的输出位置 (很多个 Y 位置)
            对 X[n, i+p, j+q, c] 求偏导:
              贡献来自所有 f: dOut[n,i,j,f] × W[p,q,c,f]
            求和 → 等于 dOut 与 W 的"转置卷积"
            形象地说: 把 W 在空间维度上翻转 180°，
                    然后让 dOut 的每个位置"广播"回它对应的输入区域

        返回:
            dX: 传给上一层的梯度
        """
        N, H_out, W_out, F = dOut.shape
        _, H, W, _ = self.X.shape

        # ─── 初始化梯度 ───
        dW = np.zeros_like(self.W)      # 权重的梯度
        db = np.sum(dOut, axis=(0, 1, 2))  # 偏置梯度: 对 dOut 在 N,H,W 上求和
        dX = np.zeros_like(self.X)      # 传给输入的梯度

        # ─── 计算 dW: X 与 dOut 做 valid 卷积 ───
        # 公式: dW[p,q,c,f] = Σ_n Σ_i Σ_j X[n,p+i,q+j,c] × dOut[n,i,j,f]
        # p,q 是滤波器内的位置，c 是输入通道，f 是输出通道
        for f in range(F):              # 遍历每个输出通道
            for c in range(self.C_in):  # 遍历每个输入通道
                for p in range(self.K): # 滤波器行
                    for q in range(self.K):  # 滤波器列
                        # 在 batch 维度求和
                        for n in range(N):
                            dW[p, q, c, f] += np.sum(
                                # X 的 [p:p+H_out, q:q+W_out] 区域 × dOut 的对应位置
                                self.X[n, p:p + H_out, q:q + W_out, c] * dOut[n, :, :, f]
                            )

        # ─── 计算 dX: dOut 与 W_rot180 做 full 卷积 (转置卷积) ───
        # W_rot180: 把 W 在空间维度 (H, W) 上翻转 180°
        #   例如 W[x,y] → W[K-1-x, K-1-y]
        W_rot = np.flip(self.W, axis=(0, 1))  # (K, K, C_in, F)

        # dX[n, i:i+K, j:j+K, :] += W_rot[:,:,:,f] × dOut[n,i,j,f]
        # 形象理解: dOut 的每个像素都是一颗"种子"，种回它对应的输入区域
        for n in range(N):
            for f in range(F):
                for i in range(H_out):
                    for j in range(W_out):
                        dX[n, i:i + self.K, j:j + self.K, :] += (
                            W_rot[:, :, :, f] * dOut[n, i, j, f]
                        )

        # ─── 参数更新 (SGD) ───
        self.W -= lr * dW
        self.b -= lr * db

        return dX  # 梯度传给上一层


# ============================================================
# 2. ReLU 激活层
# ============================================================
class ReLU:
    """
    ╔══════════════════════════════════════════════╗
    ║  ReLU (Rectified Linear Unit)               ║
    ║                                              ║
    ║  函数:  f(x) = max(0, x)                     ║
    ║  导数:  f'(x) = 1 当 x>0; 0 当 x≤0          ║
    ║                                              ║
    ║  为什么用 ReLU?                               ║
    ║  • 计算快 (只需判断 >0)                       ║
    ║  • 缓解梯度消失 (正区间导数为常数1)             ║
    ║  • 引入非线性 (否则多层 = 一层线性)             ║
    ╚══════════════════════════════════════════════╝
    """

    def __init__(self):
        self.X = None  # 缓存前向输入，反向时需要知道 X>0 的位置

    def forward(self, X):
        """
        前向: Y = max(0, X)
              所有负数变成 0，正数保持不变
        """
        self.X = X
        return np.maximum(0, X)

    def backward(self, dOut):
        """
        反向: dX = dOut × 1{X > 0}

        链式法则: ∂L/∂X = ∂L/∂Y × ∂Y/∂X
        其中 ∂Y/∂X = 1{X>0}  (X>0 的位置导数为1，X≤0 的位置导数为0)

        形象理解:
            对于 X>0 的神经元 → 梯度原样通过 (乘 1)
            对于 X≤0 的神经元 → 梯度被截断为 0 ("死了")
        """
        return dOut * (self.X > 0)


# ============================================================
# 3. 最大池化层 (MaxPool)
# ============================================================
class MaxPool:
    """
    ╔══════════════════════════════════════════════╗
    ║  MaxPool (最大池化)                          ║
    ║                                              ║
    ║  前向: 每个窗口取最大值                        ║
    ║  反向: 梯度只传给窗口内 argmax 位置，其余为 0  ║
    ║                                              ║
    ║  为什么用池化?                                ║
    ║  • 降维: 减少计算量                           ║
    ║  • 平移不变性: 轻微平移不影响最大值             ║
    ║  • 增大感受野: 后面的层能看到更大的范围          ║
    ╚══════════════════════════════════════════════╝
    """

    def __init__(self, pool_size=2):
        self.pool = pool_size        # 池化窗口大小 (默认 2×2)
        self.X = None                # 缓存输入
        self.argmax = None           # 记录每个窗口最大值的位置 (反向时需要)

    def forward(self, X):
        """
        前向: 2×2 窗口 → 取最大值

        输入:
            X: (N, H, W, C)

        输出:
            Y: (N, H/2, W/2, C)
               每个空间维度减半

        示例:
            输入窗口:       输出:
            ┌───┬───┐
            │ 1 │ 4 │     ┌───┐
            ├───┼───┤  →  │ 4 │  (4 是最大值)
            │ 2 │ 3 │     └───┘
            └───┴───┘
        """
        self.X = X
        N, H, W, C = X.shape
        # 输出尺寸 = 输入尺寸 / 池化大小 (整除)
        H_out, W_out = H // self.pool, W // self.pool

        Y = np.zeros((N, H_out, W_out, C))
        # argmax 的形状: (N, H_out, W_out, C, 2)
        #   最后一维 2 存的是 [行偏移, 列偏移]
        self.argmax = np.zeros((N, H_out, W_out, C, 2), dtype=int)

        for n in range(N):
            for c in range(C):
                for i in range(H_out):
                    for j in range(W_out):
                        # 计算窗口起始位置
                        h_start = i * self.pool
                        w_start = j * self.pool
                        # 取 2×2 窗口
                        patch = X[n, h_start:h_start + self.pool,
                                  w_start:w_start + self.pool, c]
                        # 取最大值
                        max_val = np.max(patch)
                        # 找到最大值在窗口内的位置
                        # np.argmax 返回扁平索引, unravel_index 转成 (row, col)
                        max_idx = np.unravel_index(np.argmax(patch),
                                                    (self.pool, self.pool))
                        Y[n, i, j, c] = max_val
                        self.argmax[n, i, j, c] = max_idx

        return Y

    def backward(self, dOut):
        """
        反向: 梯度只传给最大值位置

        MaxPool 的导数性质:
            输出只依赖窗口中的最大值
            所以梯度 ∂L/∂X 只在 argmax 位置为非零
            其他位置梯度为 0

        例如:
           前向: patch=[[1,4],[2,3]] → max=4, argmax=(0,1)
           反向: dOut=0.5 → dX 只在 (0,1) 处 +0.5，其他位置 +0

        这就是 MaxPool 的"路由"作用 ——
        它不会创造或累加梯度，只是把梯度"搬运"到正确位置
        """
        N, H_out, W_out, C = dOut.shape
        dX = np.zeros_like(self.X)  # 初始化为全 0

        for n in range(N):
            for c in range(C):
                for i in range(H_out):
                    for j in range(W_out):
                        # 取该窗口最大值的位置
                        h_idx, w_idx = self.argmax[n, i, j, c]
                        # 映射回原图坐标
                        h = i * self.pool + h_idx
                        w = j * self.pool + w_idx
                        # 梯度只加到最大值位置
                        dX[n, h, w, c] = dOut[n, i, j, c]
        return dX


# ============================================================
# 4. 平均池化层 (AvgPool)
# ============================================================
class AvgPool:
    """
    ╔══════════════════════════════════════════════╗
    ║  AvgPool (平均池化)                          ║
    ║                                              ║
    ║  前向: 每个窗口取平均值                        ║
    ║  反向: 梯度均匀分配给窗口内所有位置              ║
    ║                                              ║
    ║  与 MaxPool 的区别:                           ║
    ║  • MaxPool: 锐化 → 保留最显著特征              ║
    ║  • AvgPool: 平滑 → 保留整体信息                ║
    ╚══════════════════════════════════════════════╝
    """

    def __init__(self, pool_size=2):
        self.pool = pool_size
        self.X = None

    def forward(self, X):
        """
        前向: 2×2 窗口 → 取平均值

        示例:
            输入窗口:       输出:
            ┌───┬───┐
            │ 1 │ 4 │     ┌───┐
            ├───┼───┤  →  │2.5│  ( (1+4+2+3)/4 = 2.5 )
            │ 2 │ 3 │     └───┘
            └───┴───┘
        """
        self.X = X
        N, H, W, C = X.shape
        H_out, W_out = H // self.pool, W // self.pool
        Y = np.zeros((N, H_out, W_out, C))

        for n in range(N):
            for c in range(C):
                for i in range(H_out):
                    for j in range(W_out):
                        h_s = i * self.pool
                        w_s = j * self.pool
                        # 对窗口内所有值取平均
                        Y[n, i, j, c] = np.mean(
                            X[n, h_s:h_s + self.pool, w_s:w_s + self.pool, c]
                        )
        return Y

    def backward(self, dOut):
        """
        反向: 梯度均匀分配给窗口内所有位置

        AvgPool 的导数性质:
            Y = (X1 + X2 + X3 + X4) / 4
            每个 Xi 的偏导 = 1/4
            所以 dXi = dOut × 1/4

        与 MaxPool 对比:
            MaxPool: 一人独享 → 梯度给 1 个位置
            AvgPool: 平均主义 → 梯度给 pool² 个位置
        """
        N, H_out, W_out, C = dOut.shape
        dX = np.zeros_like(self.X)
        # 每个位置的梯度 = dOut / (pool * pool)
        scale = 1.0 / (self.pool * self.pool)

        for n in range(N):
            for c in range(C):
                for i in range(H_out):
                    for j in range(W_out):
                        h_s = i * self.pool
                        w_s = j * self.pool
                        # 使用 += 是为了兼容 stride < pool_size 的情况
                        # (这里 stride = pool_size，所以实际上窗口不重叠)
                        dX[n, h_s:h_s + self.pool, w_s:w_s + self.pool, c] += (
                            dOut[n, i, j, c] * scale
                        )
        return dX


# ============================================================
# 5. Flatten 展平层
# ============================================================
class Flatten:
    """
    ╔══════════════════════════════════════════════╗
    ║  Flatten 展平层                              ║
    ║                                              ║
    ║  前向: (N,H,W,C) → (N, H×W×C)               ║
    ║  反向: (N, D) → (N, H, W, C)  恢复形状        ║
    ║                                              ║
    ║  这是一个"无参数"层，作用是把卷积输出           ║
    ║  的多维张量拉成向量，喂给全连接层               ║
    ╚══════════════════════════════════════════════╝
    """

    def __init__(self):
        self.shape = None  # 存原始形状，反向时恢复

    def forward(self, X):
        """
        前向: 把每个样本展平成 1D 向量

        示例:
            X.shape = (4, 3, 3, 4)       # 4 张图, 3×3, 4 通道
            Y.shape = (4, 36)             # 拉成 36 维向量
        """
        self.shape = X.shape
        # reshape: 保持 batch 维度 N，其余维度展平
        return X.reshape(X.shape[0], -1)

    def backward(self, dOut):
        """
        反向: 恢复成原来的多维形状

        没有梯度计算，只是形状变换。因为 reshape 操作对应的
        Jacobian 矩阵是单位矩阵的排列。
        """
        return dOut.reshape(self.shape)


# ============================================================
# 6. 全连接层 (FC / Dense)
# ============================================================
class FC:
    """
    ╔══════════════════════════════════════════════╗
    ║  全连接层 (Fully Connected / Dense)          ║
    ║                                              ║
    ║  前向: Y = X @ W + b                        ║
    ║                                              ║
    ║  反向:                                        ║
    ║    dW = Xᵀ @ dOut  (除以 N 取平均)           ║
    ║    db = mean(dOut)  (在 batch 维度上求平均)   ║
    ║    dX = dOut @ Wᵀ  (传给上一层)              ║
    ║                                              ║
    ║  与卷积层的对比:                                ║
    ║    • FC: 每个输出连到所有输入 (参数多)          ║
    ║    • Conv: 局部连接 + 参数共享 (参数少)         ║
    ╚══════════════════════════════════════════════╝
    """

    def __init__(self, in_dim, out_dim):
        """
        参数:
            in_dim:  输入维度
            out_dim: 输出维度 (类别数/神经元数)
        """
        # He 初始化: 考虑 ReLU 激活
        scale = np.sqrt(2.0 / in_dim)
        self.W = np.random.randn(in_dim, out_dim) * scale
        self.b = np.zeros(out_dim)   # 偏置初始化为 0
        self.X = None                # 缓存输入，反向时需要

    def forward(self, X):
        """
        前向: Y = X @ W + b

        输入:
            X: (N, D)  N=样本数, D=输入特征数
        输出:
            Y: (N, M)  M=输出维度
        """
        self.X = X
        return X @ self.W + self.b

    def backward(self, dOut, lr=0.01):
        """
        反向传播 (含参数更新)

        链式法则推导:
            设 Y = X @ W + b, L 是损失

            ∂L/∂W = Xᵀ @ ∂L/∂Y        (矩阵微分的链式法则)
            ∂L/∂b = Σ ∂L/∂Y           (b 加到每个样本，梯度求和)
            ∂L/∂X = ∂L/∂Y @ Wᵀ        (反向传到上一层)

            除以 N 是因为我们习惯对 batch 取平均 loss
            这样学习率不依赖于 batch 大小
        """
        N = dOut.shape[0]  # batch 大小

        # dW: (D, M) = Xᵀ @ dOut，除以 N 取平均
        dW = self.X.T @ dOut / N
        # db: (M,) = dOut 在 batch 维度上求和，除以 N 取平均
        db = np.sum(dOut, axis=0) / N
        # dX: (N, D) = dOut @ Wᵀ，传到上一层
        dX = dOut @ self.W.T

        # ─── 参数更新 (SGD) ───
        self.W -= lr * dW
        self.b -= lr * db

        return dX


# ============================================================
# 7. Softmax + 交叉熵损失 (合并反向, 数值更稳定)
# ============================================================
class SoftmaxCrossEntropy:
    """
    ╔══════════════════════════════════════════════════════╗
    ║  Softmax + CrossEntropy — 分类任务标配              ║
    ║                                                      ║
    ║  前向:                                                ║
    ║    prob = softmax(logits) = e^z / Σe^z               ║
    ║    loss = -log(prob[true_class])                     ║
    ║                                                      ║
    ║  反向 (关键结论 - 数学推导出奇简洁):                    ║
    ║    ∂L/∂z = softmax(z) - y_onehot                    ║
    ║                                                      ║
    ║  直觉解释:                                            ║
    ║    预测概率 - 真实标签 = "我猜的" - "正确答案"          ║
    ║    猜对了 → 梯度趋于 0 (不需要调整)                    ║
    ║    猜错了 → 梯度驱动参数朝正确方向移动                  ║
    ║                                                      ║
    ║  为什么合并?                                           ║
    ║    分开算: softmax 反向 × CE 反向 → 中间步骤          ║
    ║    合并算: 直接 softmax(z) - y → 一步到位, 数值更稳    ║
    ╚══════════════════════════════════════════════════════╝
    """

    def __init__(self):
        self.y_true = None   # 真实标签 (整数形式, 不是 one-hot)
        self.probs = None    # Softmax 输出概率

    def forward(self, logits, y_true):
        """
        前向: 计算 Softmax 概率 + 交叉熵损失

        参数:
            logits: (N, C)  网络的原始输出 (也叫 z 或 scores)
            y_true: (N,)    真实标签，整数索引 (0, 1, 2, ...)

        数值稳定技巧:
            不是直接算 exp(z)，而是先减去 max(z)
            因为 softmax(z) = softmax(z - max)
            这样能防止 exp(大正数) → 溢出

        示例:
            logits = [[2.0, 1.0, 0.1]]     # 第一个类分数最高
            softmax → [0.66, 0.24, 0.10]   # 概率分布
            y_true = 0 → -log(0.66) = 0.41 # 损失
        """
        # ─── 数值稳定版 Softmax ───
        # 减去每行最大值，防止 exp 溢出
        # keepdims=True 保持形状，方便广播
        shifted = logits - np.max(logits, axis=1, keepdims=True)
        exp = np.exp(shifted)
        # 概率 = exp / 每行 exp 之和
        self.probs = exp / np.sum(exp, axis=1, keepdims=True)
        self.y_true = y_true

        # ─── 交叉熵损失 ───
        # loss = -1/N × Σ_n log(prob[n, y_true[n]])
        # np.arange(N) 生成 [0,1,2,...,N-1] 索引
        # self.probs[np.arange(N), y_true] 取出每个样本正确类别的概率
        N = logits.shape[0]
        loss = -np.mean(np.log(self.probs[np.arange(N), y_true] + 1e-8))
        # +1e-8 是为了防止 log(0) = -inf
        return loss

    def backward(self):
        """
        Softmax + CrossEntropy 合并反向

        核心公式 (数学推导结果):
            ∂L/∂z = (softmax(z) - y_onehot) / N

        推导思路 (简化版):
            1. 交叉熵: L = -Σ y_k × log(p_k),  p_k = e^z_k / Σ e^z_j
            2. 对 z_i 求偏导:
               ∂L/∂z_i = p_i - y_i    (利用了 Σy_k = 1 的性质)
            3. 除以 N 是因为 forward 里用了 mean

        结果解释:
            梯度的每个分量 = 预测概率 - 真实标签 (one-hot)
            形象地说: "猜得偏离真实多少，就改多少"
        """
        N = self.probs.shape[0]
        # 先拷贝概率 → 这就是 grad 的基础
        dx = self.probs.copy()
        # 真实类别位置减 1: (p_i - 1) 当 i = true_label
        # 其他位置保持原样: (p_i - 0) 当 i ≠ true_label
        dx[np.arange(N), self.y_true] -= 1
        # 除以 N 以匹配 forward 中的 mean
        return dx / N


# ============================================================
# 8. 组装完整 CNN 网络
# ============================================================
class SimpleCNN:
    """
    ╔══════════════════════════════════════════════════════════╗
    ║  完整 CNN 流水线                                         ║
    ║                                                          ║
    ║  架构:                                                    ║
    ║    输入 (N, 8, 8, 1)                                     ║
    ║    → Conv(k=3, 1→4)  → (N, 6, 6, 4)  [卷积: 提取特征]   ║
    ║    → ReLU             → (N, 6, 6, 4)  [激活: 非线性]     ║
    ║    → MaxPool(2×2)     → (N, 3, 3, 4)  [池化: 降维]      ║
    ║    → Flatten          → (N, 36)        [展平: 1D]        ║
    ║    → FC(36→2)         → (N, 2)         [全连接: 分类]     ║
    ║    → Softmax + CE     → loss           [损失]            ║
    ║                                                          ║
    ║  尺寸变化追踪:                                            ║
    ║    (8×8×1) → Conv3 → (6×6×4) → Pool2 → (3×3×4)          ║
    ║    → Flatten → 36 → FC → 2                               ║
    ╚══════════════════════════════════════════════════════════╝
    """

    def __init__(self):
        # ─── 逐层构建 ───
        # Conv: 1 输入通道 (灰度图), 4 输出通道 (4 个滤波器), 3×3 卷积核
        self.conv = Conv(in_channels=1, out_channels=4, kernel_size=3)
        self.relu = ReLU()
        self.pool = MaxPool(pool_size=2)
        self.flatten = Flatten()
        # 全连接: 3×3×4=36 维输入 → 2 个类别输出
        self.fc = FC(in_dim=36, out_dim=2)
        self.loss_fn = SoftmaxCrossEntropy()

    def forward(self, X):
        """
        前向传播: 数据依次流过每一层

        执行顺序: Conv → ReLU → MaxPool → Flatten → FC
        返回最终的 logits (未经 Softmax 的原始分数)
        """
        x = self.conv.forward(X)
        x = self.relu.forward(x)
        x = self.pool.forward(x)
        x = self.flatten.forward(x)
        x = self.fc.forward(x)
        return x  # (N, 2) — 两个类别的原始分数

    def backward(self, dOut, lr=0.01):
        """
        反向传播: 梯度从后往前依次传递

        执行顺序是 forward 的倒序:
            FC ← Flatten ← MaxPool ← ReLU ← Conv

        每一层收到上游梯度 dOut，计算并返回传给下层的梯度 dX
        """
        dx = self.fc.backward(dOut, lr)
        dx = self.flatten.backward(dx)
        dx = self.pool.backward(dx)
        dx = self.relu.backward(dx)
        dx = self.conv.backward(dx, lr)
        return dx

    def train_step(self, X, y, lr=0.01):
        """
        一次完整的训练步:

        ┌─────────┐    ┌────────┐    ┌───────┐    ┌──────────┐
        │ forward  │ → │ 计算   │ → │backward│ → │ 参数更新  │
        │ 得到logits │   │ loss   │   │ 求梯度  │   │ (SGD)   │
        └─────────┘    └────────┘    └───────┘    └──────────┘

        返回 loss 用于监控训练进度
        """
        logits = self.forward(X)              # 前向
        loss = self.loss_fn.forward(logits, y)  # 计算损失
        grad = self.loss_fn.backward()        # loss 的反向 (dL/dz)
        self.backward(grad, lr)               # 逐层反向 + 更新参数
        return loss


# ============================================================
# 9. 运行测试
# ============================================================
if __name__ == "__main__":
    """
    ╔══════════════════════════════════════════════╗
    ║  测试流程:                                    ║
    ║                                              ║
    ║  [1] 梯度检查                                ║
    ║      数值梯度: (f(w+ε) - f(w-ε)) / 2ε        ║
    ║      反向梯度: 通过反向传播计算                ║
    ║      如果两者接近 → 反向传播实现正确!           ║
    ║                                              ║
    ║  [2] 训练 10 步                               ║
    ║      观察 loss 是否持续下降                   ║
    ║                                              ║
    ║  [3] 检查最终准确率                            ║
    ╚══════════════════════════════════════════════╝
    """

    # ─── 修复 Windows GBK 终端中文输出问题 ───
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("=" * 55)
    print("  CNN 反向传播测试")
    print("=" * 55)

    # ============================================================
    # 构造测试数据
    # ============================================================
    np.random.seed(42)                          # 固定随机种子，保证可复现
    N = 4                                       # 4 个样本
    # 生成 4 张 8×8 的单通道"图像"（模拟手写数字）
    X = np.random.randn(N, 8, 8, 1) * 0.5
    # 二分类标签: [0, 1, 0, 1]
    y = np.array([0, 1, 0, 1])

    # ============================================================
    # [1] 梯度检查 — 数值梯度 vs 反向传播梯度
    # ============================================================
    print("\n[1] 梯度检查: 数值梯度 vs 反向传播梯度\n")

    net = SimpleCNN()
    eps = 1e-5   # 微小扰动，用于计算数值梯度

    # ─── 数值梯度 (中心差分法) ───
    # f'(w) ≈ (f(w+ε) - f(w-ε)) / (2ε)
    # 这个公式的误差是 O(ε²)，比单边差分 O(ε) 更精确

    # 取 conv.W 的一个参数做验证
    w_orig = net.conv.W[0, 0, 0, 0].copy()

    # f(w + ε)
    net.conv.W[0, 0, 0, 0] = w_orig + eps
    loss_plus = net.loss_fn.forward(net.forward(X), y)

    # f(w - ε)
    net.conv.W[0, 0, 0, 0] = w_orig - eps
    loss_minus = net.loss_fn.forward(net.forward(X), y)

    # 数值梯度 = (f(w+ε) - f(w-ε)) / 2ε
    numerical_grad = (loss_plus - loss_minus) / (2 * eps)

    # ─── 反向传播梯度 ───
    # 恢复原值，完整跑一次 forward + backward
    net.conv.W[0, 0, 0, 0] = w_orig
    logits = net.forward(X)
    loss = net.loss_fn.forward(logits, y)
    grad = net.loss_fn.backward()

    # 逐层反向，lr=0 表示只算梯度不更新参数
    d_fc = net.fc.backward(grad, lr=0)
    d_flat = net.flatten.backward(d_fc)
    d_pool = net.pool.backward(d_flat)
    d_relu = net.relu.backward(d_pool)
    _ = net.conv.backward(d_relu, lr=0)  # 内部计算了 dW 但未直接返回

    # ─── 手动计算 dW[0,0,0,0] 的反向传播梯度 ───
    # dW[p,q,c,f] = Σ_n Σ_i Σ_j X[n,p+i,q+j,c] × d_relu[n,i,j,f]
    # 这里 p=0, q=0, c=0, f=0
    H_out = d_relu.shape[1]  # 输出高度
    bp_grad = 0.0
    for n in range(N):
        bp_grad += np.sum(
            # X[n, 0:H_out, 0:H_out, 0]  → patch 的左上角
            # d_relu[n, :, :, 0]         → 上游梯度
            X[n, 0:H_out, 0:H_out, 0] * d_relu[n, :, :, 0]
        )

    # 打印比较结果
    print(f"  数值梯度 (中心差分):   {numerical_grad:+.6e}")
    print(f"  反向传播梯度:          {bp_grad:+.6e}")
    rel_err = abs(numerical_grad - bp_grad) / max(abs(numerical_grad), abs(bp_grad))
    print(f"  相对误差:              {rel_err:.4%}")

    if rel_err < 1e-4:
        print("  ✅ 梯度检查通过! 反向传播实现正确。")
    elif rel_err < 1e-2:
        print("  ⚠️  梯度基本一致，可能有微小数值误差。")
    else:
        print("  ❌ 梯度差异过大，反向传播可能有 bug!")

    # ============================================================
    # [2] 训练测试 — 观察 loss 是否下降
    # ============================================================
    np.random.seed(42)
    net2 = SimpleCNN()

    print("\n[2] 训练 10 步, 观察 loss 变化\n")
    print(f"  {'Step':<6} {'Loss':<10} {'趋势'}")
    print(f"  {'─'*5:6} {'─'*8:10} {'─'*20}")

    for step in range(1, 11):
        loss = net2.train_step(X, y, lr=0.05)

        # 用 | 画出 loss 的柱状图 (直观感受下降)
        if loss < 2:
            bar = "█" * int(loss * 20)
        else:
            bar = "█" * 40 + " (loss 较高)"
        print(f"  {step:<6} {loss:<10.6f} {bar}")

    # ============================================================
    # [3] 最终预测准确率
    # ============================================================
    logits_final = net2.forward(X)
    preds = np.argmax(logits_final, axis=1)  # 取概率最大的类别
    acc = np.mean(preds == y)
    print(f"\n[3] 最终准确率: {acc:.0%}")
    print(f"    预测: {preds.tolist()}")
    print(f"    真实: {y.tolist()}")

    # ============================================================
    # 最终判定
    # ============================================================
    print("\n" + "=" * 55)
    if loss < 0.5:
        print("  ✅ [PASS] 反向传播正确, Loss 持续下降, 模型在学习!")
    else:
        print("  ⚠️  [WARN] Loss 下降不明显, 可以:");
        print("     • 调大学习率 (当前 lr=0.05, 试试 0.1)")
        print("     • 增加训练步数")
        print("     • 增加数据量 (N 太小)")
    print("=" * 55)

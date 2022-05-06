import torch.nn as nn
from utils.torch import *


class Empty(nn.Module):
    def __init__(self, input_dim, out_dim, cell_type='lstm', bi_dir=False):
        super().__init__()
        self.input_dim = input_dim
        self.out_dim = out_dim
        self.cell_type = cell_type
        self.bi_dir = bi_dir
        self.mode = 'batch'
        rnn_cls = nn.LSTMCell if cell_type == 'lstm' else nn.GRUCell
        hidden_dim = out_dim // 2 if bi_dir else out_dim
        self.rnn_f = rnn_cls(self.input_dim, hidden_dim)
        if bi_dir:
            self.rnn_b = rnn_cls(self.input_dim, hidden_dim)
        self.hx, self.cx = None, None

    def set_mode(self, mode):
        self.mode = mode

    def initialize(self, batch_size=1):
        if self.mode == 'step':
            assert False, 'not sure the usage here'
            # self.hx = zeros((batch_size, self.rnn_f.hidden_size))
            # if self.cell_type == 'lstm':
            #     self.cx = zeros((batch_size, self.rnn_f.hidden_size))

    def forward(self, x):
        if self.mode == 'step':
            assert False, 'not sure the usage here'
            # self.hx, self.cx = batch_to(x.device, self.hx, self.cx)
            # if self.cell_type == 'lstm':
            #     self.hx, self.cx = self.rnn_f(x, (self.hx, self.cx))
            # else:
            #     self.hx = self.rnn_f(x, self.hx)
            # rnn_out = self.hx
        else:
            # rnn_out_f = self.batch_forward(x)
            # if not self.bi_dir:
            #     return rnn_out_f
            # rnn_out_b = self.batch_forward(x, reverse=True)
            # rnn_out = torch.cat((rnn_out_f, rnn_out_b), 2)

            # according to simpoe, here we directly output the sequence. With time shift 1
            tmp_x = x[..., 3:] * 1.  # 去除qpos的root xyz, root quat.
            rnn_out = torch.cat([tmp_x[1:], tmp_x[-1:]], dim=0)  # 做一下time shift.
        return rnn_out  # 220x1x128

    # def batch_forward(self, x, reverse=False):  # 220x1x59
    #     rnn = self.rnn_b if reverse else self.rnn_f
    #     rnn_out = []
    #     hx = zeros((x.size(1), rnn.hidden_size), device=x.device)
    #     if self.cell_type == 'lstm':
    #         cx = zeros((x.size(1), rnn.hidden_size), device=x.device)
    #     ind = reversed(range(x.size(0))) if reverse else range(x.size(0))
    #     for t in ind:
    #         if self.cell_type == 'lstm':
    #             hx, cx = rnn(x[t, ...], (hx, cx))
    #         else:
    #             hx = rnn(x[t, ...], hx)
    #         rnn_out.append(hx.unsqueeze(0))
    #     if reverse:
    #         rnn_out.reverse()
    #     rnn_out = torch.cat(rnn_out, 0)
    #     return rnn_out


if __name__ == '__main__':
    print('start')
    rnn = Empty(12, 24, 'gru', bi_dir=True)
    input = zeros(5, 3, 12)
    out = rnn(input)
    print(out.shape)

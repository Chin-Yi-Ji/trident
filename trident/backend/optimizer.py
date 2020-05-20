""" The base mixin class of  Optimizer"""
import numpy as np
from trident.backend.common import *

_session = get_session()
_backend = _session.backend
if get_session() == 'pytorch':
    import torch
    import torch.nn as nn
    from trident.backend.pytorch_backend import *
    from trident.backend.pytorch_ops import *

elif get_session() == 'tensorflow':
    _backend= 'pytorch'
    import tensorflow as tf
    from trident.backend.tensorflow_backend import *
    from trident.backend.tensorflow_ops import *




__all__ = [ 'OptimizerBase']


class OptimizerBase(object):
    """ The base mixin class of  Optimizer"""
    def adjust_learning_rate(self, new_lr, verbose=True):
        """

        Args:
            new_lr (float):  new learning rate value
            verbose (bool): if True, will print the learning rate change information.

        """
        if _backend =='pytorch':
            old_lr = self.param_groups[0]['lr']
            if old_lr != new_lr:
                self.param_groups[0]['lr'] = new_lr
                if verbose:
                    print('learning rate changed! ( form {0:.3e} to {1:.3e})'.format(old_lr, new_lr))
        elif _backend == 'tensorflow':
            old_lr = self.lr
            if old_lr != new_lr:
                if hasattr(self, '_set_hyper'):
                    if hasattr(self, '_optimizer'):
                        self._optimizer._set_hyper('learning_rate', new_lr)
                    else:
                        self._set_hyper('learning_rate', new_lr)
                elif hasattr(self, 'set_value'):
                    self.lr.set_value(new_lr)
                if verbose:
                    print('learning rate changed! ( form {0:.3e} to {1:.3e})'.format(old_lr, new_lr))


    @property
    def default_setting(self):
        """

        Returns: the default setting of this optimizer

        """
        if _backend == 'pytorch':
            return self.defaults
        elif _backend == 'tensorflow':
            return self.__dict__


    @default_setting.setter
    def default_setting(self, value):
        if _backend == 'pytorch':
            self.defaults = value
        elif _backend == 'tensorflow':
            self.__dict__.update(value)


    @property
    def parameters(self):
        """

        Returns: the weights need to train

        """
        if _backend == 'pytorch':
            return self.param_groups['params']
        elif _backend == 'tensorflow':
            return self.get_weights()


    @parameters.setter
    def parameters(self, params):
        if _backend == 'pytorch':
            self.param_groups = [{'params': list(params)}]
        elif _backend == 'tensorflow':
            self.set_weights(params)

    @property
    def lr(self):
        """

        Returns: current learning rate

        """
        if _backend ==  'pytorch':
            return self.param_groups[0]['lr']
        elif _backend == 'tensorflow':
            if hasattr(self, '_optimizer'):
                return self._optimizer._get_hyper('learning_rate').numpy()
            else:
                return self._get_hyper('learning_rate').numpy()

    @lr.setter
    def lr(self, value: float):
        if self.lr != value:
            old_lr = self.lr
            new_lr = value
            if _backend == 'pytorch':
                self.param_groups[0]['lr'] = new_lr
            elif _backend == 'tensorflow':
                if hasattr(self, '_optimizer'):
                    self._optimizer._set_hyper('learning_rate', new_lr)
                else:
                    self._set_hyper('learning_rate', new_lr)

            print('learning rate changed! ( form {0:.3e} to {1:.3e})'.format(old_lr, new_lr))

    @property
    def base_lr(self):
        """

        Returns: base learning rate means the starting learning rate (after warmup)

        """
        return self._base_lr

    @base_lr.setter
    def base_lr(self, value):
        self._base_lr = value

    def get_gradients(self, loss, params=None):
        """

        Args:
            loss (tensor): the loss function calculation result.
            params (tensor): the trainable parameters

        Returns: gradients

        """
        if _backend == 'pytorch':
            return loss.grad
        elif _backend == 'tensorflow':
            return self.get_gradients(loss, params)


    def updates(self, closure, training_context):
        """

        Args:
            closure ():
            training_context ():
        """
        if _backend == 'pytorch':
            try:
                if callable(closure):
                    loss = closure()
                    loss.backward()
            except Exception as e:
                PrintException()
        elif _backend == 'tensorflow':
            if callable(closure):
                loss = closure()



        for callback in training_context['callbacks']:
            callback.on_optimization_step_end(training_context)

    def before_batch_train(self):
        if _backend == 'pytorch':
            self.zero_grad()
        else:
            pass

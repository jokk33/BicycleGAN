# import torch.backends.cudnn as cudnn
import time
from options.train_options import TrainOptions
from data.dataloader import create_data_loader
from models.solver import create_model

opt = TrainOptions().parse()  # set CUDA_VISIBLE_DEVICES before import torch
data_loader = create_data_loader(opt)
dataset = data_loader.load_data()
dataset_size = len(data_loader)
print('#training images = %d' % dataset_size)
model = create_model(opt)

total_steps = 0

for epoch in range(1, opt.niter + opt.niter_decay + 1):
    epoch_start_time = time.time()
    save_result = True
    for i, data in enumerate(dataset):
        iter_start_time = time.time()
        total_steps += opt.batchSize
        epoch_iter = total_steps - dataset_size * (epoch - 1)
        model.update_D(data)
        if model.is_skip():
            continue
        if i % opt.disc_iters == 0:
            model.update_G()
        model.balance()

        if save_result or total_steps % opt.display_freq == 0:
            save_result = save_result or total_steps % opt.update_html_freq == 0
            save_result = False

        if total_steps % opt.print_freq == 0:
            errors = model.get_current_errors()
            t = (time.time() - iter_start_time) / opt.batchSize

        if total_steps % opt.save_latest_freq == 0:
            print('saving the latest model (epoch %d, total_steps %d)' %
                  (epoch, total_steps))
            model.save('latest')

    if epoch % opt.save_epoch_freq == 0:
        print('saving the model at the end of epoch %d, iters %d' %
              (epoch, total_steps))
        model.save('latest')
        model.save(epoch)

    print('End of epoch %d / %d \t Time Taken: %d sec' %
          (epoch, opt.niter + opt.niter_decay, time.time() - epoch_start_time))

    model.update_learning_rate()

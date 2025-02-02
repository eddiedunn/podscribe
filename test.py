import torch
print(torch.cuda.is_available())  # Should return True
print(torch.cuda.current_device())  # Should show GPU ID

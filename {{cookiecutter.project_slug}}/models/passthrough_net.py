import torch

class PassthroughNet(torch.nn.Module):
    ''' A dummy neural network that returns the input. '''

    def forward(self, x):
        return x

def test_model(model):
    TEST_DATA = torch.Tensor([[1, 2], [3, 4]])
    assert torch.equal(TEST_DATA, model(TEST_DATA))

if __name__ == '__main__':
    print('This script creates a dummy passthrough pytorch model.')
    MODEL_FILENAME = 'passthrough_net.pt'
    ARCHIVE_FILENAME = 'model.tar.gz'
    model = PassthroughNet()
    scripted = torch.jit.script(model)
    scripted.save(MODEL_FILENAME)
    print('Dummy passthrough model was saved to', MODEL_FILENAME)
    model = torch.jit.load(MODEL_FILENAME)
    model.eval()
    test_model(model)
    import tarfile
    with tarfile.open(ARCHIVE_FILENAME, "w:gz") as tar:
        tar.add(MODEL_FILENAME)
    print('Model archive was created at', ARCHIVE_FILENAME)

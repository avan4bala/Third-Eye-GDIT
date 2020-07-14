import wx
import cv2
import boto3
import os
from datetime import datetime
import Index

# vs = cv2.VideoCapture(0, cv2.CAP_DSHOW)
app = wx.App(redirect=False)
BUCKET = 'third-eye-reference-bucket'


class SnapShotPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((0, 0), 1)
        txt = 'Capture Three Sides of Your Face (in Order Respectively): Left, Right, and Front\n' \
              'Turn Your Head To The Appropriate Side and Press the \'Capture\' Button To Capture The Face Image'
        instructions = wx.StaticText(self, -1, label=txt, style=wx.ALIGN_CENTRE)
        sizer.Add(instructions, 1, wx.EXPAND | wx.ALL, 0)
        sizer.Add((0, 0), 1)
        self.row_one = wx.BoxSizer(wx.HORIZONTAL)
        self.row_one.Add(40, 200, 0)
        self.left = LiveFeedImagePanel(self, 'Left Side')
        self.row_one.Add(self.left, 1, wx.EXPAND | wx.ALL, 5)
        self.right = LiveFeedImagePanel(self, 'Right Side')
        self.row_one.Add(self.right, 1, wx.EXPAND | wx.ALL, 5)
        self.row_one.Add(40, 200, 0)

        self.row_two = wx.BoxSizer(wx.HORIZONTAL)
        self.row_two.Add(150, 200, 0)
        self.front = LiveFeedImagePanel(self, 'Front')
        self.row_two.Add(self.front, 1, wx.EXPAND | wx.ALL)
        self.row_two.Add(150, 200, 0)

        self.current_image = self.left

        sizer.Add(self.row_one, 0)
        sizer.Add(self.row_two, 0)
        sizer.Add((0, 0), 1)
        self.SetSizer(sizer)
        self.Show()

    def addSnap(self, panel):
        self.current_image.capture(panel.currentBMP(), panel.currentFrame())
        # self.sizer.Add(img, 1, wx.EXPAND | wx.ALL, 5)
        # self.Fit()
        # self.GetParent().Fit()
        # frame.Fit()
        self.Refresh()
        if self.current_image == self.left:
            self.current_image = self.right
        elif self.current_image == self.right:
            self.current_image = self.front
        else:
            self.current_image = None
            preview = self.parent.previewPanel
            preview.upload_ready()

    def snap_captures(self):
        left_img = self.left.image
        right_img = self.right.image
        front_img = self.front.image
        return [left_img, front_img, right_img]


class LiveFeedImagePanel(wx.Panel):

    def __init__(self, parent, txt):
        wx.Panel.__init__(self, parent)
        self.img = None
        self.SetMaxSize((200, 200))
        self.SetMinSize((200, 200))
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(200, 150, 0)
        text = wx.StaticText(self, label=txt, size=(200,50), style=wx.ALIGN_CENTER_HORIZONTAL)
        sizer.Add(text, 0)
        self.SetSizer(sizer)
        self.Fit()
        self.Refresh()
        self.Show()

    def capture(self, bmp, image):
        img = bmp.ConvertToImage()
        self.img = image
        img_scaled = img.Scale(200, 150)
        snap = wx.StaticBitmap(self, bitmap=wx.Bitmap(img_scaled))
        snap_item = wx.SizerItem(snap)
        sizer = self.GetSizer()
        sizer.Replace(0, snap_item)
        self.Fit()
        self.Show()

    @property
    def image(self):
        return self.img


class VideoPanel(wx.Panel):

    vs = None

    def __init__(self, parent, fps=15):
        super().__init__(parent)
        VideoPanel.vs = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        # self.vs = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        ret, frame = VideoPanel.vs.read()
        frame = cv2.flip(frame, 1)
        self.current_frame = frame
        height, width = frame.shape[:2]
        parent.SetSize((width, height))
        self.SetMaxSize((width, height))
        self.SetMinSize((width, height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        self.bmp = wx.Bitmap.FromBuffer(width, height, frame)
        self.current_bmp = self.bmp
        self.timer = wx.Timer(self)
        self.timer.Start(1000. / fps)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.NextFrame)

    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0)

    def NextFrame(self, event):
        ret, frame = VideoPanel.vs.read()
        if ret:
            frame = cv2.flip(frame, 1)
            self.current_frame = frame
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.bmp.CopyFromBuffer(frame)
            self.current_bmp = self.bmp
            self.Refresh()

    def currentBMP(self):
        return self.current_bmp

    def currentFrame(self):
        return self.current_frame


class LiveFeedPreviewPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.vid_panel = VideoPanel(self)
        sizer.Add(self.vid_panel, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)

        self.button_row = wx.BoxSizer(wx.HORIZONTAL)
        self.button_row.Add((0,0), 1)
        snap = wx.Button(self, label='Capture')
        snap.Bind(wx.EVT_BUTTON, self.snapPanelAdd)
        self.button_row.Add(snap, 0, wx.ALIGN_CENTER | wx.ALL)
        self.upload = wx.Button(self, label='Upload')
        self.upload.Bind(wx.EVT_BUTTON, self.get_snaps)
        self.button_row.Add(self.upload, 0, wx.ALIGN_CENTER | wx.ALL)
        self.button_row.Add((0, 0), 1)
        sizer.Add(self.button_row, 0, wx.EXPAND | wx.ALL, 10)
        # sizer.Add((0,0), 1)
        self.upload.Hide()
        self.Layout()
        self.Show()

    def snapPanelAdd(self, event):
        SnapShotPanel.addSnap(self.GetParent().snapPanel, self.vid_panel)

    def upload_ready(self):
        self.upload.Show()
        self.Layout()
        self.Refresh()

    def get_snaps(self, event):
        snap_panel = self.parent.snapPanel
        captures = snap_panel.snap_captures()
        self.upload_to_s3(captures)

    def upload_to_s3(self, images):
        s3_client = boto3.client('s3')
        bucket = BUCKET

        key_left = os.getlogin() + '_Left' + '.jpg'
        s3_client.put_object(ACL='public-read', Bucket=bucket, Key=key_left,
                             Body=cv2.imencode('.jpg', images[0])[1].tostring(), ContentType='image/jpeg')

        key_front = os.getlogin() + '_Front' + '.jpg'
        s3_client.put_object(ACL='public-read', Bucket=bucket, Key=key_front,
                             Body=cv2.imencode('.jpg', images[1])[1].tostring(), ContentType='image/jpeg')

        key_right = os.getlogin() + '_Right_' + '.jpg'
        s3_client.put_object(ACL='public-read', Bucket=bucket, Key=key_right,
                             Body=cv2.imencode('.jpg', images[2])[1].tostring(), ContentType='image/jpeg')

        keys = [key_left, key_front, key_right]
        Index.index_faces_keys(keys)
        response = wx.MessageBox('Upload Finished, Please Exit.', 'Result', wx.OK)


class LiveFeedMainPanel(wx.Panel):

    def __init__(self, frame):
        wx.Panel.__init__(self, frame)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.snap_panel = SnapShotPanel(self)
        self.preview_panel = LiveFeedPreviewPanel(self)
        sizer.Add(self.preview_panel, 1, wx.EXPAND | wx.ALL)
        self.preview_panel.SetMinSize(self.preview_panel.GetSize())
        self.snap_panel.SetMaxSize((500, self.preview_panel.GetSize()[1]))
        sizer.Add(self.snap_panel, 0, wx.EXPAND | wx.ALL)
        self.SetSizer(sizer)
        self.Fit()
        self.Show()

    @property
    def previewPanel(self):
        return self.preview_panel

    @property
    def snapPanel(self):
        return self.snap_panel


class LiveFeedMainFrame(wx.Frame):

    def __init__(self, origin):
        super().__init__(None, title='User Capture')
        self.origin = origin
        # self.vs = vs
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        main_panel = LiveFeedMainPanel(self)
        # self.SetSize(main_panel.GetSize())
        self.sizer.Add(main_panel, 1, wx.EXPAND)
        self.Fit()
        self.Centre()
        self.Show()

    def on_close(self, event):
        self.origin.live_feed_close(self)


# if __name__ == '__main__':
#     app = wx.App(redirect=False)
#     app.MainLoop()

# frame = LiveFeedMainFrame()
# app.MainLoop()

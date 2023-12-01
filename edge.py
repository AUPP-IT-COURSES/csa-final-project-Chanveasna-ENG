class Edge:
    def __init__(self, canvas, x, y, width, height):
        self.x = x
        self.y = y
        self.radius = 6
        self.color = "#FF0000"
        self.canvas = canvas
        self.screen_width = width
        self.screen_height = height
        self.check_collide_with_wall()
        self.dot = self.canvas.create_oval(self.x - self.radius, self.y - self.radius, self.x + self.radius, self.y + self.radius, fill=self.color, tags="dot")
        self.make_draggable()

    def make_draggable(self):
        self.canvas.tag_bind(self.dot, "<B1-Motion>", self.drag)
        # self.canvas.tag_bind(self.dot, "<ButtonRelease-1>", self.update_crop_point)

    def drag(self, event):
        # TODO: Make sure dot stays within canvas
        self.x, self.y = event.x, event.y
        self.check_collide_with_wall()
        self.canvas.coords(self.dot, self.x - self.radius, self.y - self.radius, self.x + self.radius, self.y + self.radius)

    def check_collide_with_wall(self):
        if self.x >= self.screen_width - self.radius:
            self.x = self.screen_width - self.radius
        if self.y >= self.screen_height - self.radius:
            self.y = self.screen_height - self.radius
        if self.x <= self.radius:
            self.x = self.radius
        if self.y <= self.radius:
            self.y = self.radius

    def get_position(self, event=None):
        # return (self.canvas.coords(self.dot)[0] + self.canvas.coords(self.dot)[2]) / 2, (self.canvas.coords(self.dot)[1] + self.canvas.coords(self.dot)[3]) / 2
        return self.x, self.y

from io import StringIO

class Flow:
    VTYPE = 'CAR'
    FLOWS_DIR = '/home/madis/SUMO/tmp/'
    def __init__(self, _id, route, t, n_cars):
        self.fid = _id
        self.route_name = route
        self.t = t
        self.n_cars = n_cars
        self.comment = None

    def to_xml(self):
        return f'<flow id="{self.fid}" type="{self.VTYPE}" begin="{self.t}" end="{self.t}" route="{self.route_name}" number="{self.n_cars}" departPos="free" departLane="allowed"/>'

    def flows_to_xml(flows, buf=None):
        if buf is None:
            buf = StringIO()
        buf.write('<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">\n')
        # route file should be sorted by depart time
        for flow in sorted(flows, key=lambda f: f.t):
            if flow.n_cars == 0:
                continue
            buf.write('\t'+flow.to_xml()+'\n')
            if flow.comment is not None:
                buf.write('\t<!-- ')
                for k, v in flow.comment.items():
                    buf.write(f'{k}: {v} ')
                buf.write('-->\n')
        buf.write('</routes>\n')
        buf.flush()
        return buf

if __name__ == '__main__':
    f1 = Flow('test1', 'f1', 10, 100)
    f2 = Flow('test2', 'f2', 5, 100)

    xml = Flow.flows_to_xml([f1, f2]).getvalue()
    print(xml)

import time
import queue
import socket
import logging
import threading

event_buffer = queue.Queue(maxsize=50000)
eps_dur = 60  # in seconds


class EventPublish:
    def __init__(self, evt_pub_config):
        try:
            self.ip = evt_pub_config.get('dst_ip', '')
            self.port = evt_pub_config.get('dst_port', '')
            self.size_limit = evt_pub_config.get('size_limit', 100)
            self.wait_time = evt_pub_config.get('wait_time', 60)
            self.num_threads = evt_pub_config.get('num_threads', 1)
            self.transfer_type = evt_pub_config.get('transfer_type', '')

            self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP socket
            self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
        except Exception as e:
            logging.error(f"init failed : {e}")

    def check_config(self):
        try:
            if not self.transfer_type:
                logging.error("'transfer_type' not configured in 'forwarding_config' section")
                logging.info("Configure valid transfer_type [udp, tcp]")
                return False

            elif self.transfer_type.lower() not in ['udp', 'tcp']:
                logging.error(f"Invalid transfer_type '{self.transfer_type}' configured")
                logging.info("Valid transfer_type ['udp', 'tcp']")
                return False

            elif not self.ip or not self.port:
                logging.error("'dst_ip' or 'dst_port' not configured in 'forwarding_config' section")
                logging.info("Enter proper IP and Port")
                return False

            try:
                socket.inet_aton(self.ip)
            except:
                logging.error(f"dst_ip'{self.ip}' is not valid IP address in 'forwarding_config' section")
                logging.info("Enter proper IP address")
                return False

            try:
                self.port = int(self.port)
            except:
                logging.error(f"dst_port'{self.port}' is not valid port number in 'forwarding_config' section")
                logging.info("Enter proper port number")
                return False

            return True
        except Exception as e:
            logging.error(f"Error in check config : {e}")
            return False

    def sendtoevtbuffer(self, raw_log):
        event_buffer.put(raw_log)

    def send_away(self, bunch):
        if self.transfer_type.lower() == 'udp':
            try:
                for log in bunch:
                    self.udp_sock.sendto(log, (self.ip, self.port))
                    logging.debug(f"Log sent to the IP '{self.ip}'")

                logging.debug(f"{len(bunch)} logs sent")
            except Exception as e:
                logging.error(f"Error in sending logs using UDP : {e}")
                logging.info(f"Backing off for {self.wait_time} seconds")

                if isinstance(self.wait_time, str):
                    time.sleep(int(self.wait_time))
                else:
                    time.sleep(self.wait_time)

                self.send_away(bunch)

            return 1

        elif self.transfer_type.lower() == 'tcp':
            try:
                log_bunch_str = b'\n'
                log_bunch_str += b'\n'.join(bunch)  # line by line logs sending to tcp_connector

                # TCP socket connection only once. Initial connection from exception block
                try:
                    self.tcp_sock.send(log_bunch_str)
                except socket.error as e:
                    logging.debug(f"Connection error : {e}")
                    logging.info("Connection lost. Reconnecting..")
                    self.tcp_sock.connect((self.ip, self.port))  # Reconnect
                    logging.info("Connected")
                    self.tcp_sock.send(log_bunch_str)  # Resend

                logging.debug(f"Logs sent to the IP '{self.ip}'")
                logging.debug(f"{len(bunch)} logs sent")
            except Exception as e:
                logging.error(f"Error in sending logs using TCP : {e}")
                logging.info(f"Backing off for {self.wait_time} seconds")

                if isinstance(self.wait_time, str):
                    time.sleep(int(self.wait_time))
                else:
                    time.sleep(self.wait_time)

                self.send_away(bunch)

            return 1

    def publish_process(self, event_buffer):
        bunch = []
        chktime = int(time.time()) + self.wait_time
        logtime = int(time.time()) + eps_dur
        evtcnt = 0

        while True:
            try:
                if time.time() >= logtime:
                    cnt_value = evtcnt / eps_dur
                    logging.info("EPS %.0f" % cnt_value)
                    logtime = int(time.time()) + eps_dur
                    evtcnt = 0

                log_event = event_buffer.get()
                evtcnt += 1
                bunch.append(log_event)

                if len(bunch) >= self.size_limit or time.time() >= chktime:
                    res = self.send_away(bunch)
                    if res == 1:
                        bunch = []
                        chktime = time.time() + self.wait_time
            except Exception as e:
                logging.error(f"Failed sending : {e}")

    def spawn_threads(self):
        logging.info("Creating worker threads")
        try:
            for i in range(self.num_threads):
                worker = threading.Thread(name="Evt-pub-thread-" + str(i), target=self.publish_process,
                                          args=(event_buffer,))
                worker.start()
        except Exception as e:
            logging.error(f"Creating worker threads : {e}")

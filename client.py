import json
import requests
from requests.adapters import HTTPAdapter
from ethereum.utils import sha3, big_endian_to_int, encode_int, zpad


def clean_hex(d):
    return hex(d).rstrip('L')


class EthJsonRpcClient:
    DEFAULT_GAS_PER_TX = 90000
    DEFAULT_GAS_PRICE = 50 * 10**9  # 50 gwei

    def __init__(self, host, port, contract_addr=None, tls=False):
        self.host = host
        self.port = port
        self.contract_addr = contract_addr
        self.tls = tls

        self.session = requests.Session()
        self.session.mount(self.host, HTTPAdapter(max_retries=3))

    @staticmethod
    def sha3(data):
        return hex(big_endian_to_int((sha3(data))))[2:]

    @staticmethod
    def encode_function(signature):
        prefix = big_endian_to_int(sha3(signature)[:4])
        b = zpad(encode_int(prefix), 4)
        return b.hex()

    @staticmethod
    def zpadhex(data, digit=64):
        if type(data) == int:
            d = str(data)
            h = '0' * (64 - len(d)) + d
        elif type(data) == str:
            d = data.encode().hex()
            h = '0' * (64 - len(d)) + d
        else:
            h = zpad(encode_int(data), digit).hex()
        return h

    @staticmethod
    def decode(data, types):
        i = 0
        target_addr_index_dict = {}
        results = [None for _ in range(len(types))]
        continue_flag = False
        for j in range(0, len(data), 64):
            print(data[j:j + 64].decode('utf-8'))
            for k, v in target_addr_index_dict.items():
                if j / 64 == v['index']:
                    target_addr_index_dict[k]['length'] = int(
                        data[j:j + 64].decode('utf-8'), 16)
                    continue_flag = True
                    break
                elif j / 64 == v['index'] + 1:
                    d = bytes.fromhex(
                        data[j:j + v['length'] * 2].decode('utf-8')).decode(
                            'utf-8', 'replace')
                    results[k] = d
                    continue_flag = True
                    break

            if continue_flag:
                continue_flag = False
                continue

            _type = types[i]
            if _type == 'string':
                target_addr_index_dict[i] = {}
                target_addr_index_dict[i]['index'] = int(
                    int(data[j:j + 64].decode('utf-8'), 16) / 32)
                i += 1
            elif _type == 'uint256':
                data_int = int(data[j:j + 64].decode('utf-8'), 16)
                results[i] = data_int
                i += 1
            elif _type == 'bool':
                data_bool = bool(int(data[j:j + 64].decode('utf-8')))
                results[i] = data_bool
                i += 1
        return results
        # if _type == 'string':
        #     datastr = ''
        #     for i in range(0, len(data), 2):
        #         hx = data[i:i + 2].decode('utf-8')
        #         if hx in ['00', '20']:
        #             continue
        #         d = bytes.fromhex(hx).decode('utf-8', 'replace')
        #         datastr += d
        #     return datastr
        # elif _type == 'address':
        #     data = data.decode()
        #     while data[0] == '0':
        #         data = data[1:]
        #     return '0x' + data
        # else:
        #     data = data.decode()
        #     return int(data, 16)

    def _call(self, method, params=None, _id=1):
        params = params or []
        data = {
            'jsonrpc': '2.0',
            'method': method,
            'params': params,
            'id': _id,
        }
        scheme = 'http'
        if self.tls:
            scheme += 's'
        url = '{}://{}:{}'.format(scheme, self.host, self.port)
        headers = {'Content-Type': 'application/json'}
        print(url)
        print(data)
        print(headers)
        r = self.session.post(url, headers=headers, data=json.dumps(data))
        response = r.json()
        print(response)
        return response['result']

    def build_obj(self,
                  from_address=None,
                  gas=None,
                  gas_price=None,
                  value=None,
                  data=None):
        obj = {'to': self.contract_addr}
        if from_address is not None:
            obj['from'] = from_address
        if gas is not None:
            obj['gas'] = hex(gas)
        if gas_price is not None:
            obj['gasPrice'] = clean_hex(gas_price)
        if value is not None:
            obj['value'] = value
        if data is not None:
            obj['data'] = data
        return obj

    def build_transaction(self,
                          from_address=None,
                          gas=None,
                          gas_price=None,
                          value=None,
                          data=None,
                          nonce=None):
        gas = gas or self.DEFAULT_GAS_PER_TX
        gas_price = gas_price or self.DEFAULT_GAS_PRICE
        params = {
            'from': from_address or self.eth_coinbase(),
            'to': self.contract_addr
        }
        if gas is not None:
            params['gas'] = hex(gas)
        if gas_price is not None:
            params['gasPrice'] = clean_hex(gas_price)
        if value is not None:
            params['value'] = clean_hex(value)
        if data is not None:
            params['data'] = data
        if nonce is not None:
            params['nonce'] = hex(nonce)
        return params

    def eth_coinbase(self):
        return self._call('eth_coinbase')

    def eth_call(self, obj):
        return self._call('eth_call', [obj, "latest"])

    def eth_send_transaction(self, params):
        return self._call('eth_sendTransaction', [params])

    def eth_get_transaction_by_hash(self, tx_hash):
        return self._call('eth_getTransactionByHash', [tx_hash])

    def eth_get_transaction_receipt(self, tx_hash):
        return self._call('eth_getTransactionReceipt', [tx_hash])

import os
from dotenv import load_dotenv
from ethjsonrpc import EthJsonRpc
from client import EthJsonRpcClient


def decode(data, _type):
    for i in range(0, len(data), 64):
        print(data[i:i + 64].decode('utf-8'))
    if _type == 'string':
        datastr = ''
        for i in range(0, len(data), 2):
            hx = data[i:i + 2].decode('utf-8')
            if hx in ['00', '20']:
                continue
            d = bytes.fromhex(hx).decode('utf-8', 'replace')
            datastr += d
        return datastr
    elif _type == 'address':
        data = data.decode()
        while data[0] == '0':
            data = data[1:]
        return '0x' + data
    else:
        data = data.decode()
        return int(data, 16)


def main01():
    load_dotenv()
    eth_host = os.environ.get('ETH_HOST')
    eth_port = os.environ.get('ETH_PORT')
    contract_addr = os.environ.get('CONTRACT_ADDR')
    c = EthJsonRpc(eth_host, eth_port)
    # data = c.call(contract_addr, 'rooms(uint256)', [0], ['Room'])
    # print(data)

    data = c.call(contract_addr, 'name()', [], ['string'])
    print(decode(data, 'string'))
    # data = c.call(contract_addr, 'symbol()', [], ['string'])
    # print(decode(data, 'string'))
    # data = c.call(contract_addr, 'getBlockTime()', [], ['string'])
    # print(decode(data, 'uint256'))
    # data = c.call(contract_addr, 'owner()', [], ['address'])
    # print(decode(data, 'address'))


def main02():
    load_dotenv()
    eth_host = os.environ.get('ETH_HOST')
    eth_port = os.environ.get('ETH_PORT')
    contract_addr = os.environ.get('CONTRACT_ADDR')
    c = EthJsonRpcClient(eth_host, eth_port, contract_addr)
    h = c.sha3("get()")
    print(h)
    h = c.encode_function("name()")
    print(h)
    obj = c.build_obj(data='0x' + h[:8])
    print(obj)
    result = c.eth_call(obj)
    print(result)
    print(c.decode(result[2:].encode(), ['string']))
    # obj = {
    #     'to': '0xd8eae4307f897a95f87c72bfb0a0a3f905ddf113',
    #     'data': '0x06fdde03'
    # }
    # print(obj)
    # c.eth_call(obj)


def main03():
    load_dotenv()
    eth_host = os.environ.get('ETH_HOST')
    eth_port = os.environ.get('ETH_PORT')
    contract_addr = os.environ.get('CONTRACT_ADDR')
    contract_addr = '0x6a7cead6ba1d662c7dc90ce3641416f5b2baef7c'
    print('contract_addr: ', contract_addr)
    c = EthJsonRpcClient(eth_host, eth_port, contract_addr)
    h = c.sha3("rooms(uint256)")
    data = '0x' + h[:8]
    data2 = c.zpadhex(0)
    obj = c.build_obj(data=data + data2)
    result = c.eth_call(obj)
    print(data)
    print(data2)
    print(obj)
    print(result)
    print(
        c.decode(result[2:].encode(),
                 ['string', 'string', 'bool', 'uint256', 'string', 'string']))


def main04():
    import time
    load_dotenv()
    eth_host = os.environ.get('ETH_HOST')
    eth_port = os.environ.get('ETH_PORT')
    contract_addr = os.environ.get('CONTRACT_ADDR')
    c = EthJsonRpcClient(eth_host, eth_port, contract_addr)
    h = c.sha3("addRoom(string,string,uint256,string,string)")
    data = '0x' + h[:8]
    data2 = c.zpadhex('testroom')
    data3 = c.zpadhex(1)
    obj = c.build_transaction(
        data=data + data2 + data2 + data3 + data2 + data2)
    print(obj)
    result = c.eth_send_transaction(obj)
    print(result)
    time.sleep(15)
    result2 = c.eth_get_transaction_receipt(result)
    print(result2)
    result3 = c.eth_get_transaction_by_hash(result)
    print(result3)


if __name__ == "__main__":
    # main01()
    # main02()
    main03()
    # main04()

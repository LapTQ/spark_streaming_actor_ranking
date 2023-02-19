from pyspark import SparkContext
from pyspark.streaming import StreamingContext


WINDOW_LENGTH = 60
SLIDE_INTERVAL = 30


def message_to_link(message):
    # if delimeter is ','
    if ',' in message:
        ret = eval(message)
    # if delimeter is SPACE
    else:
        ret = ((int(src), int(dst), float(wgt)) for src, dst, wgt in message.split())

    print(f'[INFO] Receive message {message}')

    return ret


def link_to_2directed_edges(link):
    src, dst, wgt = link
    return [(src, (dst, wgt)), (dst, (src, wgt))]
    # TODO src -> dst


def combine_newly_or_updated_edges(new_list, old_state):    

    ret = ([], [])
    
    for dst, wgt in new_list:
            ret[0].append(dst)
            ret[1].append(wgt)
    
    if old_state is None:
        return ret
    else:
        for dst, wgt in zip(*old_state):
            # this condition ensure the latest weight is updated
            if dst not in ret[0]:
                ret[0].append(dst)
                ret[1].append(wgt)

    return ret


def egdes_to_transitions(edges):
    src, ((destinations, weights), rank) = edges

    ret = []

    for dst, wgt in zip(destinations, weights):
        ret.append((dst, rank * wgt/sum(weights)))

    return ret


def init_rank(edges):
    src, _ = edges
    return src, 1.0


def export_result(rdd):
    print('[INFO] Printing')
    buf = []
    for vertex, rank in rdd.collect():
            buf.append(f'{vertex},{rank}')
    with open('result.csv', 'w') as f:
        f.write('\n'.join(buf))
    print('[INFO] Done')


def main():
    
    sc = SparkContext('local[4]', 'PageRank')
    ssc = StreamingContext(sc, 5)
    ssc.checkpoint("checkpoint")

    messages = ssc.sockertTextStream('localhost', 4321)  # localhost  192.168.2.20
    
    edges = messages\
        .map(message_to_link)\
            .flatMap(link_to_2directed_edges)\
                .updateStateByKey(combine_newly_or_updated_edges)

    ranks = edges.map(init_rank)

    for k in range(10):

        contribs = edges\
            .join(ranks)\
                .flatMap(egdes_to_transitions)
        
        if k == 0:
            ranks = contribs.reduceByKeyAndWindow(lambda contrib1, contrib2: contrib1 + contrib2, WINDOW_LENGTH, SLIDE_INTERVAL)
        else:
            ranks = contribs.reduceByKey(lambda contrib1, contrib2: contrib1 + contrib2)
        
        total = ranks.map(lambda x: (1, (x[1], [x[0]])))\
            .reduceByKey(lambda x, y: (x[0] + y[0], x[1] + y[1]))\
                .flatMap(lambda x: [(v, x[1][0]) for v in x[1][1]])
        
        ranks = ranks.join(total).map(lambda x: (x[0], x[1][0] / x[1][1]))

    ranks.foreachRDD(export_result)

    ranks.pprint()

    ssc.start()
    ssc.awaitTermination()


if __name__ == '__main__':
    main()
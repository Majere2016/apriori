#!/usr/bin/env python3# -*- coding: utf-8 -*-"""Created on 2017/4/13 上午10:51@author: zhechengma"""import sysimport csvimport argparseimport jsonimport osfrom collections import namedtuplefrom itertools import combinationsfrom itertools import chain#数据结构class TransactionManager(object):	#数据结构管理	def __init__(self,transactions):		#初始化数据结构		self.__num_transcation=0		self.__item=[]		self.__transcation_index_map={}		for transaction in transactions:			self.add_transaction(transaction)	def add_transaction(self,transaction):		#追加一个数据集，数据集各式['A','B']		for item in transaction:			if item not in self.__transcation_index_map:				self.__item.append(item)				self.__transcation_index_map=set()			self.__transcation_index_map[item].add(self.__num_transcation)		self.__num_transcation +=1	def calc_support(self,items):		#返回一个物品的支持度，项集类型['A','B']		#空项集是被所有集合支持的		if not items:			return 1.0		#如果集合不支持项集		if not self.num_transcation:			return 0.0		#创建一个集合索引		sum_indexes=None		for item in items:			indexes=self.__transcation_index_map.get(item)			if indexes is None:				return 0.0			if sum_indexes is None:				sum_indexes=indexes			else:				sum_indexes=sum_indexes.intersection(indexes)		return float(len(sum_indexes))/ self.__num_transcation	def initial_candidates(self):		#返回一个候选值		return [set([item]) for item in self.items]	@property	def num_transaction(self):		#返回项集的数字集合		return self.__num_transcation	@property	def items(self):		#返回项集内集合的组合		return sorted(self.__items)	@staticmethod	def create(transactions):		#创建一个项集管理用集合		if isinstance(transactions,TransactionManager):			return transactions		return TransactionManager(transactions)# Ignore name errors because these names are namedtuples.SupportRecord = namedtuple( # pylint: disable=C0103    'SupportRecord', ('items', 'support'))RelationRecord = namedtuple( # pylint: disable=C0103    'RelationRecord', SupportRecord._fields + ('ordered_statistics',))OrderedStatistic = namedtuple( # pylint: disable=C0103    'OrderedStatistic', ('items_base', 'items_add', 'confidence', 'lift',))###############内置函数##############def create_next_candidates(prev_candidates,length):	#返回一个关联分析的候选集作为一个列表	item_set=set()	for candidate in prev_candidates:		for item in candidate:			item_set.add(item)	items = sorted(item_set)	#创建一个临时项集，这些会被过滤	tmp_next_candidates = (set(x) for x in combinations(items,length))	#返回所有项集如果下一个候选的长度是2	#因为他们的内容项一样	if length<3:		return list(tmp_next_candidates)	#赛选项集	#在先验项集	next_candidates = [		candidate for candidate in tmp_next_candidates	    if all(			True if set(x) in prev_candidates else False			for x in combinations(candidate,length-1))	]	return next_candidatesdef gen_support_records(transaction_manager,min_support,**kwargs):	#返回给定系数支持度的生成器	max_length=kwargs.get('max_length')	_create_next_candidates=kwargs.get(		'_create_next_candidates',create_next_candidates	)	candidates=transaction_manager.intial_candidates()	length=1	while candidates:		relations=set()		for relation_cadidate in candidates:			support = transaction_manager.calc_support(relation_cadidate)			if support < min_support:				continue			candidates_set=set(relation_cadidate)			relations.add(candidates_set)			yield SupportRecord(candidates_set,support)		length +=1		if max_length and length > max_length:			break		candidates=_create_next_candidates(relations,length)def gen_ordered_statistics(transaction_manager,record):	#返回一个统计技术常数	items=record.items	for combination_set in combinations(sorted(items),len(items)-1):		items_base = set(combination_set)		items_add = set(items.difference(items_base))		confidence=(			record.support/transaction_manager.calc_support(items_base)		)		lift=confidence/transaction_manager.calc_support(items_add)		yield OrderedStatistic(			set(items_base),set(items_add),confidence,lift		)def filter_ordered_statistics(ordered_statistics,**kwargs):	#重要说明：min_confidece是最小关系数值	#重要说明：最小提升度是最小关系数值	min_confidence=kwargs.get('min_confidence',0.0)	min_lift=kwargs.get('min_lift',0.0)	for ordered_statistic in ordered_statistics:		if ordered_statistic.confidence<min_confidence:			print(ordered_statistic.confidence)			continue		if ordered_statistic.lift<min_lift:			print(ordered_statistic.lift)			continue		yield ordered_statistic######################计算过程#####################def apriori(transactions,**kwargs):	#设置参数	min_support=kwargs.get('min_support',0.005)	min_confidence = kwargs.get ( 'min_confidence' , 0.01 )	min_lift = kwargs.get ( 'min_lift' , 0.01 )	max_length = kwargs.get ( 'max_length' , None )	# 检查参数	if min_support <= 0 :		raise ValueError ( 'minimum support must be > 0' )	# For testing.	_gen_support_records = kwargs.get (		'_gen_support_records' , gen_support_records )	_gen_ordered_statistics = kwargs.get (		'_gen_ordered_statistics' , gen_ordered_statistics )	_filter_ordered_statistics = kwargs.get (		'_filter_ordered_statistics' , filter_ordered_statistics )	# 计算支持度	transaction_manager = TransactionManager.create ( transactions )	support_records = _gen_support_records (		transaction_manager , min_support , max_length = max_length )	# 	计算有序统计。	for support_record in support_records :		ordered_statistics = list (			_filter_ordered_statistics (				_gen_ordered_statistics ( transaction_manager , support_record ) ,				min_confidence = min_confidence ,				min_lift = min_lift ,			)		)		if not ordered_statistics :			continue		yield RelationRecord (			support_record.items , support_record.support , ordered_statistics )####################应用计算###################def parse_args(argv):	output_funcs = {        'json': dump_as_json,        'tsv': dump_as_two_item_tsv,    }    default_output_func_key = 'json'    parser = argparse.ArgumentParser()    parser.add_argument(        '-v', '--version', action='version',		version='%(prog)s {0}'.format(__version__))    parser.add_argument(        'input', metavar='inpath', nargs='*',        help='Input transaction file (default: stdin).',        type=argparse.FileType('r'), default=[sys.stdin])    parser.add_argument(        '-o', '--output', metavar='outpath',        help='Output file (default: stdout).',        type=argparse.FileType('w'), default=sys.stdout)    parser.add_argument(        '-l', '--max-length', metavar='int',        help='Max length of relations (default: infinite).',        type=int, default=None)    parser.add_argument(        '-s', '--min-support', metavar='float',        help='Minimum support ratio (must be > 0, default: 0.1).',        type=float, default=0.1)    parser.add_argument(        '-c', '--min-confidence', metavar='float',        help='Minimum confidence (default: 0.5).',        type=float, default=0.5)    parser.add_argument(        '-t', '--min-lift', metavar='float',        help='Minimum lift (default: 0.0).',        type=float, default=0.0)    parser.add_argument(        '-d', '--delimiter', metavar='str',        help='Delimiter for items of transactions (default: tab).',        type=str, default='\t')    parser.add_argument(        '-f', '--out-format', metavar='str',        help='Output format ({0}; default: {1}).'.format(            ', '.join(output_funcs.keys()), default_output_func_key),        type=str, choices=output_funcs.keys(), default=default_output_func_key)    args = parser.parse_args(argv)    args.output_func = output_funcs[args.out_format]    return argsdef load_transactions(input_file, **kwargs):    """    Load transactions and returns a generator for transactions.    Arguments:        input_file -- An input file.    Keyword arguments:        delimiter -- The delimiter of the transaction.    """    delimiter = kwargs.get('delimiter', '\t')    for transaction in csv.reader(input_file, delimiter=delimiter):        yield transaction if transaction else ['']def dump_as_json(record, output_file):    """    Dump an relation record as a json value.    Arguments:        record -- A RelationRecord instance to dump.        output_file -- A file to output.    """    def default_func(value):        """        Default conversion for JSON value.        """        if isinstance(value, frozenset):            return sorted(value)        raise TypeError(repr(value) + " is not JSON serializable")    converted_record = record._replace(        ordered_statistics=[x._asdict() for x in record.ordered_statistics])    json.dump(        converted_record._asdict(), output_file,        default=default_func, ensure_ascii=False)    output_file.write(os.linesep)def dump_as_two_item_tsv(record, output_file):    """    Dump a relation record as TSV only for 2 item relations.    Arguments:        record -- A RelationRecord instance to dump.        output_file -- A file to output.    """    for ordered_stats in record.ordered_statistics:        if len(ordered_stats.items_base) != 1:            continue        if len(ordered_stats.items_add) != 1:            continue        output_file.write('{0}\t{1}\t{2:.8f}\t{3:.8f}\t{4:.8f}{5}'.format(            list(ordered_stats.items_base)[0], list(ordered_stats.items_add)[0],            record.support, ordered_stats.confidence, ordered_stats.lift,            os.linesep))def main(**kwargs):    """    Executes Apriori algorithm and print its result.    """    # For tests.    _parse_args = kwargs.get('_parse_args', parse_args)    _load_transactions = kwargs.get('_load_transactions', load_transactions)    _apriori = kwargs.get('_apriori', apriori)    args = _parse_args(sys.argv[1:])    transactions = _load_transactions(        chain(*args.input), delimiter=args.delimiter)    result = _apriori(        transactions,        max_length=args.max_length,        min_support=args.min_support,        min_confidence=args.min_confidence)    for record in result:        args.output_func(record, args.output)if __name__ == '__main__':	main()
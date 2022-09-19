# This code is mostly adapted from the AllenNLP Seq2Seq DatasetReader:
# https://github.com/allenai/allennlp-models/blob/main/allennlp_models/generation/dataset_readers/seq2seq.py

import copy
import csv
import logging
from typing import Dict, Iterable, List, Optional

from allennlp.common.util import START_SYMBOL, END_SYMBOL
from allennlp.common.checks import ConfigurationError
from allennlp.common.file_utils import cached_path
from allennlp.data import DatasetReader, Instance
from allennlp.data.fields import Field, LabelField, TextField
from allennlp.data.token_indexers import TokenIndexer, SingleIdTokenIndexer
from allennlp.data.tokenizers import Token, Tokenizer, WhitespaceTokenizer, SpacyTokenizer
from tqdm import tqdm

logger = logging.getLogger(__name__)


@DatasetReader.register("yoga_seq2seq")
class Seq2SeqReader(DatasetReader):
    def __init__(
            self,
            tokenizer: Tokenizer = None,
            source_token_indexers: Dict[str, TokenIndexer] = None,
            target_token_indexers: Dict[str, TokenIndexer] = None,
            source_add_start_token: bool = False,
            source_add_end_token: bool = False,
            target_add_start_token: bool = False,
            target_add_end_token: bool = False,
            start_symbol: str = START_SYMBOL,
            end_symbol: str = END_SYMBOL,
            delimiter: str = "\t",
            **kwargs
    ):
        super().__init__(**kwargs)
        self._tokenizer = tokenizer or SpacyTokenizer()
        self._source_token_indexers = source_token_indexers or {"tokens": SingleIdTokenIndexer()}
        self._target_token_indexers = target_token_indexers or self._source_token_indexers

        self._source_add_start_token = source_add_start_token
        self._source_add_end_token = source_add_end_token
        self._target_add_start_token = target_add_start_token
        self._target_add_end_token = target_add_end_token
        self._start_token: Optional[Token] = None
        self._end_token: Optional[Token] = None

        if source_add_start_token or source_add_end_token or target_add_start_token or target_add_end_token:
            self._check_start_end_tokens(start_symbol, end_symbol, self._tokenizer)

        self._start_token = Token(start_symbol)
        self._end_token = Token(end_symbol)

        self._delimiter = delimiter

    def _read(self, file_path: str):
        with open(cached_path(file_path), "r") as data_file:
            logger.info("Reading instances from lines in file at: %s", file_path)
            for line_num, row in tqdm(enumerate(data_file)):
                row = row.strip().split(self._delimiter)
                if len(row) != 2:
                    raise ConfigurationError(
                        "Invalid line format: %s (line number %d)" % (row, line_num + 1)
                    )
                source_sequence, target_sequence = row
                if len(source_sequence) == 0 or len(target_sequence) == 0:
                    continue
                yield self.text_to_instance(source_sequence, target_sequence)

    def text_to_field(self, str_to_tokenize: str) -> TextField:
        tokenized_str = self._tokenizer.tokenize(str_to_tokenize)
        if self._source_add_start_token:
            tokenized_str.insert(0, copy.deepcopy(self._start_token))
        if self._source_add_end_token:
            tokenized_str.append(copy.deepcopy(self._end_token))
        return TextField(tokenized_str)

    def text_to_instance(
            self, source_string: str, target_string: Optional[str] = None,
    ) -> Instance:  # type: ignore
        source_field = self.text_to_field(source_string)

        if target_string:
            target_field = self.text_to_field(target_string)
            return Instance({"source_tokens": source_field, "target_tokens": target_field})
        else:
            return Instance({"source_tokens": source_field})

    def apply_token_indexers(self, instance: Instance) -> None:
        instance.fields["source_tokens"]._token_indexers = self._source_token_indexers  # type: ignore
        if "target_tokens" in instance.fields:
            instance.fields["target_tokens"]._token_indexers = self._target_token_indexers  # type: ignore

    def _check_start_end_tokens(
            self, start_symbol: str, end_symbol: str, tokenizer: Tokenizer
    ) -> None:
        """Check that `tokenizer` correctly appends `start_symbol` and `end_symbol` to the
        sequence without splitting them. Raises a `ValueError` if this is not the case.
        """

        tokens = tokenizer.tokenize(start_symbol + " " + end_symbol)
        err_msg = (
            f"Bad start or end symbol ('{start_symbol}', '{end_symbol}') "
            f"for tokenizer {self._tokenizer}"
        )
        try:
            start_token, end_token = tokens[0], tokens[-1]
        except IndexError:
            raise ValueError(err_msg)
        if start_token.text != start_symbol or end_token.text != end_symbol:
            raise ValueError(err_msg)

"""Test reading of TDMS files with DAQmx data
"""

import logging
import unittest
import numpy as np

from nptdms import tdms
from nptdms.test.util import TestFile, hexlify_value, string_hexlify


class DaqmxDataTests(unittest.TestCase):
    def setUp(self):
        logging.getLogger(tdms.__name__).setLevel(logging.DEBUG)

    def test_single_channel_i16(self):
        """ Test loading a DAQmx file with a single channel of I16 data
        """

        scaler_metadata = daqmx_scaler_metadata(0, 3, 0)
        metadata = combine_metadata(
            root_metadata(),
            group_metadata(),
            daqmx_channel_metadata("Channel1", 4, [2], [scaler_metadata]))
        data = (
            "01 00"
            "02 00"
            "FF FF"
            "FE FF"
        )

        test_file = TestFile()
        test_file.add_segment(metadata, data, segment_toc())
        tdms_data = test_file.load()

        data = tdms_data.object("Group", "Channel1").raw_data

        self.assertEqual(data.dtype, np.int16)
        np.testing.assert_array_equal(data, [1, 2, -1, -2])

    def test_single_channel_u16(self):
        """ Test loading a DAQmx file with a single channel of U16 data
        """

        scaler_metadata = daqmx_scaler_metadata(0, 2, 0)
        metadata = combine_metadata(
            root_metadata(),
            group_metadata(),
            daqmx_channel_metadata("Channel1", 4, [2], [scaler_metadata]))
        data = (
            # Data for segment
            "01 00"
            "02 00"
            "FF FF"
            "FE FF"
        )

        test_file = TestFile()
        test_file.add_segment(metadata, data, segment_toc())
        tdms_data = test_file.load()

        data = tdms_data.object("Group", "Channel1").raw_data

        self.assertEqual(data.dtype, np.uint16)
        np.testing.assert_array_equal(data, [1, 2, 2**16 - 1, 2**16 - 2])

    def test_single_channel_i32(self):
        """ Test loading a DAQmx file with a single channel of I32 data
        """

        scaler_metadata = daqmx_scaler_metadata(0, 5, 0)
        metadata = combine_metadata(
            root_metadata(),
            group_metadata(),
            daqmx_channel_metadata("Channel1", 4, [4], [scaler_metadata]))
        data = (
            # Data for segment
            "01 00 00 00"
            "02 00 00 00"
            "FF FF FF FF"
            "FE FF FF FF"
        )

        test_file = TestFile()
        test_file.add_segment(metadata, data, segment_toc())
        tdms_data = test_file.load()

        data = tdms_data.object("Group", "Channel1").raw_data

        self.assertEqual(data.dtype, np.int32)
        np.testing.assert_array_equal(data, [1, 2, -1, -2])

    def test_single_channel_u32(self):
        """ Test loading a DAQmx file with a single channel of U32 data
        """

        scaler_metadata = daqmx_scaler_metadata(0, 4, 0)
        metadata = combine_metadata(
            root_metadata(),
            group_metadata(),
            daqmx_channel_metadata("Channel1", 4, [4], [scaler_metadata]))
        data = (
            # Data for segment
            "01 00 00 00"
            "02 00 00 00"
            "FF FF FF FF"
            "FE FF FF FF"
        )

        test_file = TestFile()
        test_file.add_segment(metadata, data, segment_toc())
        tdms_data = test_file.load()

        data = tdms_data.object("Group", "Channel1").raw_data

        self.assertEqual(data.dtype, np.uint32)
        np.testing.assert_array_equal(data, [1, 2, 2**32 - 1, 2**32 - 2])

    def test_two_channel_i16(self):
        """ Test loading a DAQmx file with two channels of I16 data
        """

        scaler_1 = daqmx_scaler_metadata(0, 3, 0)
        scaler_2 = daqmx_scaler_metadata(0, 3, 2)
        metadata = combine_metadata(
            root_metadata(),
            group_metadata(),
            daqmx_channel_metadata("Channel1", 4, [4], [scaler_1]),
            daqmx_channel_metadata("Channel2", 4, [4], [scaler_2]))
        data = (
            # Data for segment
            "01 00"
            "11 00"
            "02 00"
            "12 00"
            "03 00"
            "13 00"
            "04 00"
            "14 00"
        )

        test_file = TestFile()
        test_file.add_segment(metadata, data, segment_toc())
        tdms_data = test_file.load()

        data_1 = tdms_data.object("Group", "Channel1").raw_data
        self.assertEqual(data_1.dtype, np.int16)
        np.testing.assert_array_equal(data_1, [1, 2, 3, 4])

        data_2 = tdms_data.object("Group", "Channel2").raw_data
        self.assertEqual(data_2.dtype, np.int16)
        np.testing.assert_array_equal(data_2, [17, 18, 19, 20])

    def test_mixed_channel_widths(self):
        """ Test loading a DAQmx file with channels with different widths
        """

        scaler_1 = daqmx_scaler_metadata(0, 1, 0)
        scaler_2 = daqmx_scaler_metadata(0, 3, 1)
        scaler_3 = daqmx_scaler_metadata(0, 5, 3)
        metadata = combine_metadata(
            root_metadata(),
            group_metadata(),
            daqmx_channel_metadata("Channel1", 4, [7], [scaler_1]),
            daqmx_channel_metadata("Channel2", 4, [7], [scaler_2]),
            daqmx_channel_metadata("Channel3", 4, [7], [scaler_3]))
        data = (
            # Data for segment
            "01 11 00 21 00 00 00"
            "02 12 00 22 00 00 00"
            "03 13 00 23 00 00 00"
            "04 14 00 24 00 00 00"
        )

        test_file = TestFile()
        test_file.add_segment(metadata, data, segment_toc())
        tdms_data = test_file.load()

        data_1 = tdms_data.object("Group", "Channel1").raw_data
        self.assertEqual(data_1.dtype, np.int8)
        np.testing.assert_array_equal(data_1, [1, 2, 3, 4])

        data_2 = tdms_data.object("Group", "Channel2").raw_data
        self.assertEqual(data_2.dtype, np.int16)
        np.testing.assert_array_equal(data_2, [17, 18, 19, 20])

        data_3 = tdms_data.object("Group", "Channel3").raw_data
        self.assertEqual(data_3.dtype, np.int32)
        np.testing.assert_array_equal(data_3, [33, 34, 35, 36])

    def test_multiple_scalers_with_same_type(self):
        """ Test loading a DAQmx file with one channel containing multiple
            format changing scalers of the same type
        """

        scaler_metadata = [
            daqmx_scaler_metadata(0, 3, 0),
            daqmx_scaler_metadata(1, 3, 2)]
        metadata = combine_metadata(
            root_metadata(),
            group_metadata(),
            daqmx_channel_metadata("Channel1", 4, [4], scaler_metadata))
        data = (
            # Data for segment
            "01 00"
            "11 00"
            "02 00"
            "12 00"
            "03 00"
            "13 00"
            "04 00"
            "14 00"
        )

        test_file = TestFile()
        test_file.add_segment(metadata, data, segment_toc())
        tdms_data = test_file.load()
        channel = tdms_data.object("Group", "Channel1")

        scaler_0_data = channel.raw_scaler_data(0)
        self.assertEqual(scaler_0_data.dtype, np.int16)
        np.testing.assert_array_equal(scaler_0_data, [1, 2, 3, 4])

        scaler_1_data = channel.raw_scaler_data(1)
        self.assertEqual(scaler_1_data.dtype, np.int16)
        np.testing.assert_array_equal(scaler_1_data, [17, 18, 19, 20])

    def test_multiple_scalers_with_different_types(self):
        """ Test loading a DAQmx file with one channel containing multiple
            format changing scalers of different types
        """

        scaler_metadata = [
            daqmx_scaler_metadata(0, 1, 0),
            daqmx_scaler_metadata(1, 3, 1),
            daqmx_scaler_metadata(2, 5, 3)]
        metadata = combine_metadata(
            root_metadata(),
            group_metadata(),
            daqmx_channel_metadata("Channel1", 4, [7], scaler_metadata))
        data = (
            # Data for segment
            "01 11 00 21 00 00 00"
            "02 12 00 22 00 00 00"
            "03 13 00 23 00 00 00"
            "04 14 00 24 00 00 00"
        )

        test_file = TestFile()
        test_file.add_segment(metadata, data, segment_toc())
        tdms_data = test_file.load()
        channel = tdms_data.object("Group", "Channel1")

        scaler_0_data = channel.raw_scaler_data(0)
        self.assertEqual(scaler_0_data.dtype, np.int8)
        np.testing.assert_array_equal(scaler_0_data, [1, 2, 3, 4])

        scaler_1_data = channel.raw_scaler_data(1)
        self.assertEqual(scaler_1_data.dtype, np.int16)
        np.testing.assert_array_equal(scaler_1_data, [17, 18, 19, 20])

        scaler_2_data = channel.raw_scaler_data(2)
        self.assertEqual(scaler_2_data.dtype, np.int32)
        np.testing.assert_array_equal(scaler_2_data, [33, 34, 35, 36])


def combine_metadata(*args):
    num_objects_hex = hexlify_value("<I", len(args))
    return num_objects_hex + "".join(args)


def segment_toc():
    return (
        "kTocMetaData", "kTocRawData", "kTocNewObjList", "kTocDAQmxRawData")


def root_metadata():
    return (
        # Length of the object path
        "01 00 00 00"
        # Object path (/)
        "2F"
        # Raw data index
        "FF FF FF FF"
        # Num properties
        "00 00 00 00")


def group_metadata():
    return (
        # Length of the object path
        "08 00 00 00"
        # Object path (/'Group')
        "2F 27 47 72"
        "6F 75 70 27"
        # Raw data index
        "FF FF FF FF"
        # Num properties
        "00 00 00 00")


def daqmx_scaler_metadata(scale_id, type_id, byte_offset):
    return (
        # DAQmx data type (type ids don't match TDMS types)
        hexlify_value("<I", type_id) +
        # Raw buffer index
        "00 00 00 00" +
        # Raw byte offset
        hexlify_value("<I", byte_offset) +
        # Sample format bitmap (don't know what this is for...)
        "00 00 00 00" +
        # Scale ID
        hexlify_value("<I", scale_id))


def daqmx_channel_metadata(
        channel_name, num_values,
        raw_data_widths, scaler_metadata):
    path = "/'Group'/'" + channel_name + "'"
    return (
        # Length of the object path
        hexlify_value("<I", len(path)) +
        # Object path
        string_hexlify(path) +
        # Raw data index (DAQmx)
        "69 12 00 00"
        # Data type (DAQmx)
        "FF FF FF FF"
        # Array  dimension
        "01 00 00 00" +
        # Number of values (chunk size)
        hexlify_value("<Q", num_values) +
        # Scaler metadata
        hexlify_value("<I", len(scaler_metadata)) +
        "".join(scaler_metadata) +
        # Raw data width vector size
        hexlify_value("<I", len(raw_data_widths)) +
        # Raw data width values
        "".join(hexlify_value("<I", v) for v in raw_data_widths) +
        # Number of properties (0)
        "00 00 00 00")

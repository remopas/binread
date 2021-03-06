from sys import byteorder
import unittest
import struct
import binread


class TestTypes(unittest.TestCase):
    def test_f64_little(self):
        value = binread.F64(byteorder="little").read_field(
            binread.reader.ByteReader(struct.pack("<d", 5.2)), {}
        )
        self.assertAlmostEqual(value, 5.2)

    def test_f64_big(self):
        value = binread.F64(byteorder="big").read_field(
            binread.reader.ByteReader(struct.pack(">d", 5.2)), {}
        )
        self.assertAlmostEqual(value, 5.2)

    def test_f32_little(self):
        value = binread.F32(byteorder="little").read_field(
            binread.reader.ByteReader(struct.pack("<f", 5.2)), {}
        )
        self.assertAlmostEqual(value, 5.2, places=6)

    def test_f32_big(self):
        value = binread.F32(byteorder="big").read_field(
            binread.reader.ByteReader(struct.pack(">f", 5.2)), {}
        )
        self.assertAlmostEqual(value, 5.2, places=6)

    def test_f16_little(self):
        value = binread.F16(byteorder="little").read_field(
            binread.reader.ByteReader(struct.pack("<e", 5.2)), {}
        )
        self.assertAlmostEqual(value, 5.2, places=2)

    def test_f16_big(self):
        value = binread.F16(byteorder="big").read_field(
            binread.reader.ByteReader(struct.pack(">e", 5.2)), {}
        )
        self.assertAlmostEqual(value, 5.2, places=2)

    def test_u64_big(self):
        self.assertEqual(
            (2**64 - 1),
            binread.U64(byteorder="big").read_field(
                binread.reader.ByteReader(struct.pack(">Q", 2**64 - 1)), {}
            ),
        )

    def test_u64_little(self):
        self.assertEqual(
            (2**64 - 1),
            binread.U64(byteorder="little").read_field(
                binread.reader.ByteReader(struct.pack("<Q", 2**64 - 1)), {}
            ),
        )

    def test_u32_big(self):
        self.assertEqual(
            (2**32 - 1),
            binread.U32(byteorder="big").read_field(
                binread.reader.ByteReader(struct.pack(">L", 2**32 - 1)), {}
            ),
        )

    def test_u32_little(self):
        self.assertEqual(
            (2**32 - 1),
            binread.U32(byteorder="little").read_field(
                binread.reader.ByteReader(struct.pack("<L", 2**32 - 1)), {}
            ),
        )

    def test_u16_big(self):
        self.assertEqual(
            (2**16 - 1),
            binread.U16(byteorder="big").read_field(
                binread.reader.ByteReader(struct.pack(">H", 2**16 - 1)), {}
            ),
        )

    def test_u16_little(self):
        self.assertEqual(
            (2**16 - 1),
            binread.U16(byteorder="little").read_field(
                binread.reader.ByteReader(struct.pack("<H", 2**16 - 1)), {}
            ),
        )

    def test_u8_big(self):
        self.assertEqual(
            (2**8 - 1),
            binread.U8(byteorder="big").read_field(
                binread.reader.ByteReader(struct.pack(">B", 2**8 - 1)), {}
            ),
        )

    def test_u8_little(self):
        self.assertEqual(
            (2**8 - 1),
            binread.U8(byteorder="little").read_field(
                binread.reader.ByteReader(struct.pack("<B", 2**8 - 1)), {}
            ),
        )

    def test_i64_big(self):
        self.assertEqual(
            (-(2**63) + 1),
            binread.I64(byteorder="big").read_field(
                binread.reader.ByteReader(struct.pack(">q", -(2**63) + 1)), {}
            ),
        )

    def test_i64_little(self):
        self.assertEqual(
            (-(2**63) + 1),
            binread.I64(byteorder="little").read_field(
                binread.reader.ByteReader(struct.pack("<q", -(2**63) + 1)), {}
            ),
        )

    def test_i32_big(self):
        self.assertEqual(
            (-(2**31) + 1),
            binread.I32(byteorder="big").read_field(
                binread.reader.ByteReader(struct.pack(">l", -(2**31) + 1)), {}
            ),
        )

    def test_i32_little(self):
        self.assertEqual(
            (-(2**31) + 1),
            binread.I32(byteorder="little").read_field(
                binread.reader.ByteReader(struct.pack("<l", -(2**31) + 1)), {}
            ),
        )

    def test_i16_big(self):
        self.assertEqual(
            (-(2**15) + 1),
            binread.I16(byteorder="big").read_field(
                binread.reader.ByteReader(struct.pack(">h", -(2**15) + 1)), {}
            ),
        )

    def test_i16_little(self):
        self.assertEqual(
            (-(2**15) + 1),
            binread.I16(byteorder="little").read_field(
                binread.reader.ByteReader(struct.pack("<h", -(2**15) + 1)), {}
            ),
        )

    def test_i8_big(self):
        self.assertEqual(
            (-(2**7) + 1),
            binread.I8(byteorder="big").read_field(
                binread.reader.ByteReader(struct.pack(">b", -(2**7) + 1)), {}
            ),
        )

    def test_i8_little(self):
        self.assertEqual(
            (-(2**7) + 1),
            binread.I8(byteorder="little").read_field(
                binread.reader.ByteReader(struct.pack("<b", -(2**7) + 1)), {}
            ),
        )

    def test_array(self):
        self.assertEqual(
            ([1, 2, 3, 4, 5]),
            binread.Array(element=binread.U16, length=5).read_field(
                binread.reader.ByteReader(struct.pack("5H", 1, 2, 3, 4, 5)), {}
            ),
        )

    def test_array_variable_terminated(self):
        self.assertEqual(
            ([1, 2, 3, 4, 0]),
            binread.Array(element=binread.U16, terminator=0).read_field(
                binread.reader.ByteReader(struct.pack("6H", 1, 2, 3, 4, 0, 10)), {}
            ),
        )

    def test_array_function(self):
        self.assertEqual(
            ([1, 2, 3, 4, 0]),
            binread.Array(element=binread.U16, terminator=0).read_field(
                binread.reader.ByteReader(struct.pack("6H", 1, 2, 3, 4, 0, 10)), {}
            ),
        )

    def test_array_struct(self):
        value = binread.Array(
            binread.Format({"array": binread.Array(binread.U16, length=5)}),
            length=2,
        ).read_field(
            binread.reader.ByteReader(struct.pack("10H", 1, 2, 3, 4, 5, 1, 2, 3, 4, 5)),
            {},
        )

        self.assertEqual(
            ([{"array": [1, 2, 3, 4, 5]}, {"array": [1, 2, 3, 4, 5]}]), value
        )

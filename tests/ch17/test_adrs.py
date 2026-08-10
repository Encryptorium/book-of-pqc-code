"""Tests for the ADRS address structure."""

from slh_dsa.adrs import ADRS, WOTS_HASH, WOTS_PK, TREE, FORS_TREE


class TestADRSFields:
    def test_initial_state_is_zeroed(self) -> None:
        a = ADRS()
        assert a.to_bytes() == b"\x00" * 32

    def test_layer_address(self) -> None:
        a = ADRS()
        a.set_layer_address(5)
        assert a.get_layer_address() == 5

    def test_tree_address(self) -> None:
        a = ADRS()
        a.set_tree_address(0x123456789ABCDEF0)
        assert a.get_tree_address() == 0x123456789ABCDEF0

    def test_keypair_address(self) -> None:
        a = ADRS()
        a.set_keypair_address(42)
        assert a.get_keypair_address() == 42

    def test_chain_address(self) -> None:
        a = ADRS()
        a.set_chain_address(7)
        assert a.get_chain_address() == 7

    def test_hash_address(self) -> None:
        a = ADRS()
        a.set_hash_address(15)
        assert a.get_hash_address() == 15

    def test_tree_height_and_index(self) -> None:
        a = ADRS()
        a.set_tree_height(3)
        a.set_tree_index(100)
        assert a.get_tree_height() == 3
        assert a.get_tree_index() == 100


class TestADRSTypeZeroing:
    def test_set_type_zeros_bytes_20_to_31(self) -> None:
        a = ADRS()
        a.set_keypair_address(99)
        a.set_chain_address(77)
        a.set_hash_address(55)
        a.set_type(WOTS_HASH)
        assert a.get_keypair_address() == 0
        assert a.get_chain_address() == 0
        assert a.get_hash_address() == 0

    def test_set_type_preserves_layer_and_tree(self) -> None:
        a = ADRS()
        a.set_layer_address(3)
        a.set_tree_address(12345)
        a.set_keypair_address(42)
        a.set_type(TREE)
        assert a.get_layer_address() == 3
        assert a.get_tree_address() == 12345
        assert a.get_type() == TREE


class TestADRSCopy:
    def test_copy_is_independent(self) -> None:
        a = ADRS()
        a.set_layer_address(7)
        b = a.copy()
        b.set_layer_address(99)
        assert a.get_layer_address() == 7
        assert b.get_layer_address() == 99

    def test_copy_preserves_all_fields(self) -> None:
        a = ADRS()
        a.set_layer_address(1)
        a.set_tree_address(2)
        a.set_type(WOTS_PK)
        a.set_keypair_address(3)
        b = a.copy()
        assert b.to_bytes() == a.to_bytes()


class TestADRSCompress:
    def test_compress_length(self) -> None:
        a = ADRS()
        assert len(a.compress()) == 22

    def test_compress_extracts_correct_bytes(self) -> None:
        a = ADRS()
        full = bytearray(32)
        for i in range(32):
            full[i] = i
        a._data[:] = full
        c = a.compress()
        # ADRS[3] || ADRS[8:16] || ADRS[19] || ADRS[20:32]
        expected = bytes([3]) + bytes(range(8, 16)) + bytes([19]) + bytes(range(20, 32))
        assert c == expected


class TestADRSToBytes:
    def test_length_is_32(self) -> None:
        a = ADRS()
        assert len(a.to_bytes()) == 32

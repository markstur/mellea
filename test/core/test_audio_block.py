"""Unit tests for AudioBlock class."""

import pytest

from mellea.core import AudioBlock


class TestAudioBlockFromDataURI:
    """Test AudioBlock creation from data URI."""

    def test_audio_block_from_wav_data_uri(self):
        """Test AudioBlock creation from WAV data URI."""
        # Minimal valid WAV file (44 bytes header + some data)
        wav_base64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
        audio = AudioBlock(f"data:audio/wav;base64,{wav_base64}")
        assert audio.format == "wav"
        assert audio.value is not None

    def test_audio_block_from_mp3_data_uri(self):
        """Test AudioBlock creation from MP3 data URI."""
        # Minimal MP3-like data (ID3 tag)
        mp3_base64 = "SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4LjI5LjEwMA=="
        # Format is extracted as-is from URI (no alias mapping)
        audio = AudioBlock(f"data:audio/mpeg;base64,{mp3_base64}")
        assert audio.format == "mpeg"
        assert audio.value is not None

    def test_audio_block_from_flac_data_uri(self):
        """Test AudioBlock creation from FLAC data URI."""
        # Minimal FLAC file (fLaC signature)
        flac_base64 = "ZkxhQwAA"
        audio = AudioBlock(f"data:audio/flac;base64,{flac_base64}")
        assert audio.format == "flac"
        assert audio.value is not None

    def test_audio_block_from_ogg_data_uri(self):
        """Test AudioBlock creation from OGG data URI."""
        # Minimal OGG file (OggS signature)
        ogg_base64 = "T2dnUwACAAAAAAAAAA=="
        audio = AudioBlock(f"data:audio/ogg;base64,{ogg_base64}")
        assert audio.format == "ogg"
        assert audio.value is not None

    def test_audio_block_from_opus_data_uri(self):
        """Test AudioBlock creation from OPUS data URI."""
        # Minimal OPUS-like data
        opus_base64 = "T2dnUwACAAAAAAAAAABPcHVzSGVhZA=="
        audio = AudioBlock(f"data:audio/opus;base64,{opus_base64}")
        assert audio.format == "opus"
        assert audio.value is not None

    def test_audio_block_from_m4a_data_uri(self):
        """Test AudioBlock creation from M4A data URI."""
        # Minimal M4A file (ftyp signature)
        m4a_base64 = "AAAAIGZ0eXBNNEEgAAAAAE00QQ=="
        # Format is extracted as-is from URI (no alias mapping)
        audio = AudioBlock(f"data:audio/mp4;base64,{m4a_base64}")
        assert audio.format == "mp4"
        assert audio.value is not None


class TestAudioBlockWithExplicitFormat:
    """Test AudioBlock with explicit format parameter."""

    def test_audio_block_with_explicit_format(self):
        """Test AudioBlock with explicit format parameter."""
        wav_base64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
        audio = AudioBlock(wav_base64, format="wav")
        assert audio.format == "wav"
        assert audio.value is not None

    def test_explicit_format_overrides_uri(self):
        """Test that explicit format overrides data URI format."""
        wav_base64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
        # URI says mp3, but explicit format says wav
        audio = AudioBlock(f"data:audio/mp3;base64,{wav_base64}", format="wav")
        assert audio.format == "wav"


class TestAudioBlockInvalidBase64:
    """Test AudioBlock rejects invalid base64."""

    def test_audio_block_invalid_base64(self):
        """Test AudioBlock rejects invalid base64."""
        with pytest.raises(AssertionError):
            AudioBlock("not-base64!!!", format="wav")

    def test_audio_block_invalid_base64_with_uri(self):
        """Test AudioBlock rejects invalid base64 even with data URI."""
        with pytest.raises(AssertionError):
            AudioBlock("data:audio/wav;base64,not-valid-base64!!!")


class TestAudioBlockAnyFormat:
    """Test AudioBlock accepts any format (validation deferred to backend)."""

    def test_audio_block_exotic_format_explicit(self):
        """Test AudioBlock accepts exotic formats via explicit parameter."""
        # Should NOT raise - format validation is deferred to backend
        audio = AudioBlock(
            "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=",
            format="midi",
        )
        assert audio.format == "midi"

    def test_audio_block_exotic_format_from_uri(self):
        """Test AudioBlock accepts exotic formats from data URI."""
        # Should NOT raise - format validation is deferred to backend
        audio = AudioBlock(
            "data:audio/midi;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
        )
        assert audio.format == "midi"

    def test_audio_block_custom_format(self):
        """Test AudioBlock accepts custom/experimental formats."""
        audio = AudioBlock(
            "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=",
            format="custom_codec",
        )
        assert audio.format == "custom_codec"


class TestAudioBlockMissingFormat:
    """Test AudioBlock requires format for raw base64."""

    def test_audio_block_missing_format(self):
        """Test AudioBlock requires format for raw base64."""
        with pytest.raises(ValueError, match="Audio format must be specified"):
            AudioBlock("UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=")


class TestFormatDetectionFromDataURI:
    """Test format auto-detection from data URI."""

    def test_format_detection_from_data_uri(self):
        """Test format auto-detection from data URI."""
        # Standard formats - extracted as-is (no alias mapping)
        assert AudioBlock.get_format_from_data_uri("data:audio/wav;base64,...") == "wav"
        assert (
            AudioBlock.get_format_from_data_uri("data:audio/mpeg;base64,...") == "mpeg"
        )
        assert AudioBlock.get_format_from_data_uri("data:audio/mp3;base64,...") == "mp3"
        assert (
            AudioBlock.get_format_from_data_uri("data:audio/flac;base64,...") == "flac"
        )
        assert AudioBlock.get_format_from_data_uri("data:audio/ogg;base64,...") == "ogg"
        assert (
            AudioBlock.get_format_from_data_uri("data:audio/opus;base64,...") == "opus"
        )
        assert AudioBlock.get_format_from_data_uri("data:audio/mp4;base64,...") == "mp4"
        assert (
            AudioBlock.get_format_from_data_uri("data:audio/x-m4a;base64,...")
            == "x-m4a"
        )
        # Exotic/custom formats also work
        assert (
            AudioBlock.get_format_from_data_uri("data:audio/midi;base64,...") == "midi"
        )
        assert (
            AudioBlock.get_format_from_data_uri("data:audio/custom;base64,...")
            == "custom"
        )

    def test_format_detection_raw_base64(self):
        """Test format detection returns None for raw base64."""
        assert AudioBlock.get_format_from_data_uri("raw-base64-string") is None
        assert AudioBlock.get_format_from_data_uri("") is None

    def test_format_detection_invalid_uri(self):
        """Test format detection with malformed URI."""
        assert AudioBlock.get_format_from_data_uri("data:video/mp4;base64,...") is None
        assert AudioBlock.get_format_from_data_uri("no-base64-prefix") is None


class TestIsValidBase64Audio:
    """Test is_valid_base64_audio static method."""

    def test_valid_base64(self):
        """Test valid base64 string."""
        assert AudioBlock.is_valid_base64_audio("SGVsbG8gV29ybGQ=") is True

    def test_valid_base64_with_uri(self):
        """Test valid base64 with data URI prefix."""
        assert (
            AudioBlock.is_valid_base64_audio("data:audio/wav;base64,SGVsbG8gV29ybGQ=")
            is True
        )

    def test_invalid_base64(self):
        """Test invalid base64 string."""
        assert AudioBlock.is_valid_base64_audio("not-valid-base64!!!") is False

    def test_invalid_base64_with_uri(self):
        """Test invalid base64 with data URI prefix."""
        assert (
            AudioBlock.is_valid_base64_audio("data:audio/wav;base64,not-valid!!!")
            is False
        )

    def test_base64_with_padding(self):
        """Test base64 string needing padding."""
        # "test" in base64 is "dGVzdA==" (already padded)
        assert AudioBlock.is_valid_base64_audio("dGVzdA==") is True

    def test_base64_without_padding(self):
        """Test base64 string without padding."""
        # "test" without padding would be "dGVzdA" (length 6, needs 2 padding chars)
        assert AudioBlock.is_valid_base64_audio("dGVzdA") is True


class TestAudioBlockMetadata:
    """Test AudioBlock with metadata."""

    def test_audio_block_metadata(self):
        """Test AudioBlock with metadata."""
        wav_base64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
        meta = {"duration": 5.2, "sample_rate": 44100}
        audio = AudioBlock(f"data:audio/wav;base64,{wav_base64}", meta=meta)
        assert audio._meta == meta

    def test_audio_block_no_metadata(self):
        """Test AudioBlock without metadata defaults to empty dict."""
        wav_base64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
        audio = AudioBlock(f"data:audio/wav;base64,{wav_base64}")
        assert audio._meta == {}


class TestAudioBlockRepr:
    """Test AudioBlock string representation."""

    def test_audio_block_repr(self):
        """Test AudioBlock __repr__ method."""
        wav_base64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
        audio = AudioBlock(f"data:audio/wav;base64,{wav_base64}")
        repr_str = repr(audio)
        assert "AudioBlock" in repr_str
        assert "data:audio/wav;base64" in repr_str


class TestAudioBlockInheritance:
    """Test AudioBlock inherits from CBlock."""

    def test_audio_block_is_cblock(self):
        """Test AudioBlock is a subclass of CBlock."""
        from mellea.core import CBlock

        wav_base64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
        audio = AudioBlock(f"data:audio/wav;base64,{wav_base64}")
        assert isinstance(audio, CBlock)

    def test_audio_block_value_property(self):
        """Test AudioBlock inherits value property from CBlock."""
        wav_base64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
        audio = AudioBlock(f"data:audio/wav;base64,{wav_base64}")
        assert audio.value is not None
        assert wav_base64 in audio.value

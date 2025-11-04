"""Unit tests for cycloidFun module.

Tests the core mathematical functions and parameter validation
for the cycloidal gearbox generation.
"""

import pytest
import math
import sys
import os

# Add parent directory to path to import cycloidFun
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Note: These tests test the mathematical functions independently
# Full integration tests with FreeCAD would require FreeCAD to be installed


class TestConstants:
    """Test module-level constants."""

    def test_constants_defined(self):
        """Verify all constants are properly defined."""
        from cycloidFun import (
            MIN_TOOTH_COUNT, MAX_TOOTH_COUNT,
            DEG_TO_RAD, RAD_TO_DEG,
            MIN_ECCENTRICITY, MIN_ROLLER_DIAMETER,
            MIN_SHAFT_DIAMETER
        )

        assert MIN_TOOTH_COUNT == 3
        assert MAX_TOOTH_COUNT == 50
        assert abs(DEG_TO_RAD - math.pi / 180.0) < 1e-10
        assert abs(RAD_TO_DEG - 180.0 / math.pi) < 1e-10
        assert MIN_ECCENTRICITY > 0
        assert MIN_ROLLER_DIAMETER > 0
        assert MIN_SHAFT_DIAMETER > 0


class TestGeometricFunctions:
    """Test basic geometric utility functions."""

    def test_to_polar(self):
        """Test Cartesian to polar coordinate conversion."""
        from cycloidFun import to_polar

        # Test (1, 0) -> (1, 0)
        r, theta = to_polar(1, 0)
        assert abs(r - 1.0) < 1e-10
        assert abs(theta - 0.0) < 1e-10

        # Test (0, 1) -> (1, pi/2)
        r, theta = to_polar(0, 1)
        assert abs(r - 1.0) < 1e-10
        assert abs(theta - math.pi/2) < 1e-10

        # Test (3, 4) -> (5, atan(4/3))
        r, theta = to_polar(3, 4)
        assert abs(r - 5.0) < 1e-10
        assert abs(theta - math.atan2(4, 3)) < 1e-10

    def test_to_rect(self):
        """Test polar to Cartesian coordinate conversion."""
        from cycloidFun import to_rect

        # Test (1, 0) -> (1, 0)
        x, y = to_rect(1, 0)
        assert abs(x - 1.0) < 1e-10
        assert abs(y - 0.0) < 1e-10

        # Test (1, pi/2) -> (0, 1)
        x, y = to_rect(1, math.pi/2)
        assert abs(x - 0.0) < 1e-10
        assert abs(y - 1.0) < 1e-10

        # Test (5, atan(4/3)) -> (3, 4)
        x, y = to_rect(5, math.atan2(4, 3))
        assert abs(x - 3.0) < 1e-10
        assert abs(y - 4.0) < 1e-10

    def test_clean1(self):
        """Test clamping function."""
        from cycloidFun import clean1

        assert clean1(0.5) == 0.5
        assert clean1(1.5) == 1.0
        assert clean1(-1.5) == -1.0
        assert clean1(0.999) == 0.999
        assert clean1(-0.999) == -0.999


class TestParameterValidation:
    """Test parameter validation functions."""

    def test_valid_default_parameters(self):
        """Test that default parameters pass validation."""
        from cycloidFun import generate_default_parameters, validate_parameters

        params = generate_default_parameters()
        # Should not raise any exception
        validate_parameters(params)

    def test_tooth_count_too_low(self):
        """Test validation fails for tooth count < MIN_TOOTH_COUNT."""
        from cycloidFun import (
            generate_default_parameters,
            validate_parameters,
            ParameterValidationError
        )

        params = generate_default_parameters()
        params["tooth_count"] = 2

        with pytest.raises(ParameterValidationError, match="tooth_count must be"):
            validate_parameters(params)

    def test_tooth_count_too_high(self):
        """Test validation fails for tooth count > MAX_TOOTH_COUNT."""
        from cycloidFun import (
            generate_default_parameters,
            validate_parameters,
            ParameterValidationError
        )

        params = generate_default_parameters()
        params["tooth_count"] = 100

        with pytest.raises(ParameterValidationError, match="tooth_count must be"):
            validate_parameters(params)

    def test_negative_eccentricity(self):
        """Test validation fails for negative eccentricity."""
        from cycloidFun import (
            generate_default_parameters,
            validate_parameters,
            ParameterValidationError
        )

        params = generate_default_parameters()
        params["eccentricity"] = -1.0

        with pytest.raises(ParameterValidationError, match="eccentricity"):
            validate_parameters(params)

    def test_roller_diameter_too_small(self):
        """Test validation fails for very small roller diameter."""
        from cycloidFun import (
            generate_default_parameters,
            validate_parameters,
            ParameterValidationError
        )

        params = generate_default_parameters()
        params["roller_diameter"] = 0.01

        with pytest.raises(ParameterValidationError, match="roller_diameter"):
            validate_parameters(params)

    def test_diameter_smaller_than_roller_circle(self):
        """Test validation fails when Diameter < roller_circle_diameter."""
        from cycloidFun import (
            generate_default_parameters,
            validate_parameters,
            ParameterValidationError
        )

        params = generate_default_parameters()
        params["Diameter"] = 50
        params["roller_circle_diameter"] = 80

        with pytest.raises(ParameterValidationError, match="Diameter.*must be >"):
            validate_parameters(params)

    def test_pressure_angle_out_of_range(self):
        """Test validation for pressure angle limits."""
        from cycloidFun import (
            generate_default_parameters,
            validate_parameters,
            ParameterValidationError
        )

        params = generate_default_parameters()

        # Too low
        params["pressure_angle_limit"] = 5.0
        with pytest.raises(ParameterValidationError, match="pressure_angle_limit"):
            validate_parameters(params)

        # Too high
        params["pressure_angle_limit"] = 90.0
        with pytest.raises(ParameterValidationError, match="pressure_angle_limit"):
            validate_parameters(params)


class TestCycloidalMath:
    """Test cycloidal gear mathematical functions."""

    def test_calcyp_normal_case(self):
        """Test calcyp function with normal parameters."""
        from cycloidFun import calcyp

        result = calcyp(1.0, 0.5, 2.0, 11)
        assert isinstance(result, float)
        # Result should be a valid angle in radians
        assert -math.pi <= result <= math.pi

    def test_calcyp_zero_denominator(self):
        """Test calcyp handles division by near-zero denominator."""
        from cycloidFun import calcyp

        # This should raise ValueError for division by zero
        # Finding exact parameters that cause this requires solving the equation
        # For now, we test that the function doesn't crash with normal inputs
        try:
            result = calcyp(1.0, math.pi/2, 2.0, 11)
            assert isinstance(result, float)
        except ValueError:
            # Expected if denominator is too small
            pass

    def test_calc_x_and_calc_y(self):
        """Test calc_x and calc_y functions."""
        from cycloidFun import calc_x, calc_y

        p = 7.27
        roller_diameter = 9.4
        eccentricity = 2.0
        tooth_count = 11
        angle = 0.5

        x = calc_x(p, roller_diameter, eccentricity, tooth_count, angle)
        y = calc_y(p, roller_diameter, eccentricity, tooth_count, angle)

        assert isinstance(x, float)
        assert isinstance(y, float)
        # Values should be reasonable (not NaN or infinite)
        assert not math.isnan(x)
        assert not math.isnan(y)
        assert not math.isinf(x)
        assert not math.isinf(y)

    def test_calculate_pressure_angle(self):
        """Test pressure angle calculation."""
        from cycloidFun import calculate_pressure_angle

        p = 7.27
        roller_diameter = 9.4
        tooth_count = 11
        angle = 0.5

        pressure_angle = calculate_pressure_angle(p, roller_diameter, tooth_count, angle)

        assert isinstance(pressure_angle, float)
        # Pressure angle should be in reasonable range (degrees)
        assert -90 <= pressure_angle <= 90

    def test_calculate_pressure_angle_clamping(self):
        """Test that pressure angle calculation clamps asin argument."""
        from cycloidFun import calculate_pressure_angle

        # Use parameters that might cause out-of-range asin
        # The function should clamp and log warning instead of crashing
        try:
            result = calculate_pressure_angle(0.1, 20.0, 11, 0.0)
            assert isinstance(result, float)
        except ValueError:
            # Acceptable if division by zero is detected
            pass

    def test_calculate_radii(self):
        """Test epitrochoid radii calculation."""
        from cycloidFun import calculate_radii

        pin_count = 11
        eccentricity = 2.0
        outer_diameter = 100.0
        pin_diameter = 9.4

        r1, r2 = calculate_radii(pin_count, eccentricity, outer_diameter, pin_diameter)

        assert isinstance(r1, float)
        assert isinstance(r2, float)
        assert r1 > 0
        assert r2 > 0
        # Check relationship: r1 + r2 should equal outer_radius
        assert abs(r1 + r2 - outer_diameter/2) < 1e-10

    def test_calculate_radii_clamping(self):
        """Test that calculate_radii clamps values to valid ranges."""
        from cycloidFun import calculate_radii, MIN_TOOTH_COUNT, MAX_TOOTH_COUNT

        # Too few teeth - should clamp to MIN_TOOTH_COUNT
        r1, r2 = calculate_radii(1, 2.0, 100.0, 9.4)
        expected_r1 = (MIN_TOOTH_COUNT - 1) * 50 / MIN_TOOTH_COUNT
        expected_r2 = 50 / MIN_TOOTH_COUNT
        assert abs(r1 - expected_r1) < 1e-10
        assert abs(r2 - expected_r2) < 1e-10

        # Too many teeth - should clamp to MAX_TOOTH_COUNT
        r1, r2 = calculate_radii(100, 2.0, 100.0, 9.4)
        expected_r1 = (MAX_TOOTH_COUNT - 1) * 50 / MAX_TOOTH_COUNT
        expected_r2 = 50 / MAX_TOOTH_COUNT
        assert abs(r1 - expected_r1) < 1e-10
        assert abs(r2 - expected_r2) < 1e-10


class TestDefaultParameters:
    """Test default parameter generation."""

    def test_generate_default_parameters(self):
        """Test that default parameters are valid and complete."""
        from cycloidFun import generate_default_parameters

        params = generate_default_parameters()

        # Check all required keys are present
        required_keys = [
            "eccentricity", "tooth_count", "driver_disk_hole_count",
            "driver_hole_diameter", "driver_circle_diameter",
            "line_segment_count", "tooth_pitch", "Diameter",
            "roller_diameter", "roller_circle_diameter",
            "pressure_angle_limit", "pressure_angle_offset",
            "base_height", "disk_height", "shaft_diameter",
            "key_diameter", "key_flat_diameter", "Height", "clearance",
            "min_rad", "max_rad"
        ]

        for key in required_keys:
            assert key in params, f"Missing required parameter: {key}"

        # Check types and basic validity
        assert isinstance(params["tooth_count"], int)
        assert params["tooth_count"] >= 3
        assert params["eccentricity"] > 0
        assert params["roller_diameter"] > 0
        assert params["Diameter"] > params["roller_circle_diameter"]


class TestThreadSafety:
    """Test thread-safe lock mechanism."""

    def test_lock_exists(self):
        """Test that the thread lock is defined."""
        import cycloidFun

        assert hasattr(cycloidFun, '_generate_parts_lock')

    def test_parameter_validation_error_exists(self):
        """Test that custom exception is defined."""
        from cycloidFun import ParameterValidationError

        # Should be a ValueError subclass
        assert issubclass(ParameterValidationError, ValueError)

        # Should be instantiable
        err = ParameterValidationError("test")
        assert str(err) == "test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

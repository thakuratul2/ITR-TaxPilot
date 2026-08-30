"""Comprehensive unit tests for Assessment Year tax rules."""

import pytest

from app.tax.rules import (
    AY2025_26RuleSet,
    AY2026_27RuleSet,
    AY2027_28RuleSet,
    DeductionCatalog,
    TaxRegime,
    registry,
)


class TestRuleRegistry:
    """Test the rule registry functionality."""

    def test_registry_singleton(self):
        """Test that registry is a singleton."""
        from app.tax.rules import registry as registry2
        assert registry is registry2

    def test_registered_assessment_years(self):
        """Test that all expected AYs are registered."""
        registered_ays = registry.list_registered_ays()
        assert "2025-26" in registered_ays
        assert "2026-27" in registered_ays
        assert "2027-28" in registered_ays

    def test_get_rule_set(self):
        """Test retrieving rule sets by AY."""
        ay_25_26 = registry.get_rule_set("2025-26")
        assert ay_25_26 is not None
        assert isinstance(ay_25_26, AY2025_26RuleSet)

        ay_26_27 = registry.get_rule_set("2026-27")
        assert ay_26_27 is not None
        assert isinstance(ay_26_27, AY2026_27RuleSet)

        ay_27_28 = registry.get_rule_set("2027-28")
        assert ay_27_28 is not None
        assert isinstance(ay_27_28, AY2027_28RuleSet)

    def test_unsupported_ay(self):
        """Test that unsupported AY returns None."""
        unsupported = registry.get_rule_set("2099-00")
        assert unsupported is None

    def test_is_ay_supported(self):
        """Test AY support check."""
        assert registry.is_ay_supported("2025-26") is True
        assert registry.is_ay_supported("2026-27") is True
        assert registry.is_ay_supported("2027-28") is True
        assert registry.is_ay_supported("2099-00") is False


class TestAY2025_26Rules:
    """Test AY 2025-26 specific rules."""

    def setup_method(self):
        """Setup test instance."""
        self.rules = AY2025_26RuleSet()

    def test_metadata(self):
        """Test rule metadata."""
        assert self.rules.metadata.assessment_year == "2025-26"
        assert self.rules.metadata.rule_code == "AY_2025_26"
        assert self.rules.metadata.effective_from == "2024-04-01"
        assert self.rules.metadata.effective_to == "2025-03-31"

    def test_old_regime_slabs(self):
        """Test old regime tax slabs."""
        slabs = self.rules.get_slabs(TaxRegime.OLD)
        assert len(slabs) == 4

        # Check slab boundaries
        assert slabs[0].lower_limit == 0
        assert slabs[0].upper_limit == 250000
        assert slabs[0].rate_percent == 0

        assert slabs[1].lower_limit == 250000
        assert slabs[1].upper_limit == 500000
        assert slabs[1].rate_percent == 5

        assert slabs[2].lower_limit == 500000
        assert slabs[2].upper_limit == 1000000
        assert slabs[2].rate_percent == 20

        assert slabs[3].lower_limit == 1000000
        assert slabs[3].upper_limit is None
        assert slabs[3].rate_percent == 30

    def test_new_regime_slabs(self):
        """Test new regime tax slabs."""
        slabs = self.rules.get_slabs(TaxRegime.NEW)
        assert len(slabs) == 6

        # Check key slab boundaries
        assert slabs[0].lower_limit == 0
        assert slabs[0].upper_limit == 300000
        assert slabs[0].rate_percent == 0

        assert slabs[1].lower_limit == 300000
        assert slabs[1].upper_limit == 700000
        assert slabs[1].rate_percent == 5

        assert slabs[5].lower_limit == 1500000
        assert slabs[5].upper_limit is None
        assert slabs[5].rate_percent == 30

    def test_standard_deduction(self):
        """Test standard deduction amount."""
        old_sd = self.rules.get_standard_deduction(TaxRegime.OLD)
        assert old_sd.amount == 50000
        assert TaxRegime.OLD in old_sd.applicable_regimes

        new_sd = self.rules.get_standard_deduction(TaxRegime.NEW)
        assert new_sd.amount == 50000
        assert TaxRegime.NEW in new_sd.applicable_regimes

    def test_rebate_87a_old_regime(self):
        """Test Section 87A rebate for old regime."""
        rebate = self.rules.get_rebate_87a(TaxRegime.OLD)
        assert rebate.max_taxable_income == 500000
        assert rebate.max_rebate_amount == 12500
        assert TaxRegime.OLD in rebate.applicable_regimes

    def test_rebate_87a_new_regime(self):
        """Test Section 87A rebate for new regime."""
        rebate = self.rules.get_rebate_87a(TaxRegime.NEW)
        assert rebate.max_taxable_income == 700000
        assert rebate.max_rebate_amount == 25000
        assert TaxRegime.NEW in rebate.applicable_regimes

    def test_surcharge_rates(self):
        """Test surcharge rate configuration."""
        surcharges = self.rules.get_surcharge_rates()
        assert len(surcharges) == 4

        # Check key thresholds
        assert surcharges[0].income_threshold == 50000000
        assert surcharges[0].rate_percent == 10

        assert surcharges[3].income_threshold == 500000000
        assert surcharges[3].rate_percent == 37

    def test_cess_rate(self):
        """Test Health & Education Cess rate."""
        assert self.rules.get_cess_rate() == 4.0

    def test_deduction_eligibility_old_regime(self):
        """Test deduction eligibility under old regime."""
        assert self.rules.is_deduction_eligible("80C", TaxRegime.OLD) is True
        assert self.rules.is_deduction_eligible("80D", TaxRegime.OLD) is True
        assert self.rules.is_deduction_eligible("24(b)", TaxRegime.OLD) is True
        assert self.rules.is_deduction_eligible("80CCD(2)", TaxRegime.OLD) is True

    def test_deduction_eligibility_new_regime(self):
        """Test deduction eligibility under new regime."""
        assert self.rules.is_deduction_eligible("80C", TaxRegime.NEW) is False
        assert self.rules.is_deduction_eligible("80D", TaxRegime.NEW) is False
        assert self.rules.is_deduction_eligible("24(b)", TaxRegime.NEW) is False
        assert self.rules.is_deduction_eligible("80CCD(2)", TaxRegime.NEW) is True

    def test_invalid_regime(self):
        """Test handling of invalid regime."""
        with pytest.raises(ValueError):
            self.rules.get_slabs("INVALID")


class TestAY2026_27Rules:
    """Test AY 2026-27 specific rules."""

    def setup_method(self):
        """Setup test instance."""
        self.rules = AY2026_27RuleSet()

    def test_metadata(self):
        """Test rule metadata."""
        assert self.rules.metadata.assessment_year == "2026-27"
        assert self.rules.metadata.rule_code == "AY_2026_27"
        assert self.rules.metadata.effective_from == "2025-04-01"
        assert self.rules.metadata.effective_to == "2026-03-31"

    def test_standard_deduction_increase(self):
        """Test standard deduction increased to ₹75,000."""
        old_sd = self.rules.get_standard_deduction(TaxRegime.OLD)
        assert old_sd.amount == 75000

        new_sd = self.rules.get_standard_deduction(TaxRegime.NEW)
        assert new_sd.amount == 75000

    def test_slab_boundaries(self):
        """Test that slab boundaries are maintained from AY 2025-26."""
        old_slabs = self.rules.get_slabs(TaxRegime.OLD)
        new_slabs = self.rules.get_slabs(TaxRegime.NEW)

        # Old regime slabs should be same as AY 2025-26
        assert len(old_slabs) == 4
        assert old_slabs[0].upper_limit == 250000

        # New regime slabs should be same as AY 2025-26
        assert len(new_slabs) == 6
        assert new_slabs[0].upper_limit == 300000

    def test_rebate_limits(self):
        """Test that rebate limits are maintained."""
        old_rebate = self.rules.get_rebate_87a(TaxRegime.OLD)
        assert old_rebate.max_taxable_income == 500000
        assert old_rebate.max_rebate_amount == 12500

        new_rebate = self.rules.get_rebate_87a(TaxRegime.NEW)
        assert new_rebate.max_taxable_income == 700000
        assert new_rebate.max_rebate_amount == 25000


class TestAY2027_28Rules:
    """Test AY 2027-28 template structure."""

    def setup_method(self):
        """Setup test instance."""
        self.rules = AY2027_28RuleSet()

    def test_metadata_template(self):
        """Test that metadata indicates template status."""
        assert self.rules.metadata.assessment_year == "2027-28"
        assert "Template" in self.rules.metadata.rule_name
        assert "Pending" in self.rules.metadata.last_amended

    def test_placeholder_slabs(self):
        """Test that placeholder slabs are present."""
        old_slabs = self.rules.get_slabs(TaxRegime.OLD)
        new_slabs = self.rules.get_slabs(TaxRegime.NEW)

        # Should have placeholder values
        assert len(old_slabs) > 0
        assert len(new_slabs) > 0

    def test_placeholder_standard_deduction(self):
        """Test that placeholder standard deduction is present."""
        sd = self.rules.get_standard_deduction(TaxRegime.OLD)
        assert sd.amount == 75000  # Placeholder from AY 2026-27

    def test_structure_completeness(self):
        """Test that all required methods are implemented."""
        assert hasattr(self.rules, 'get_slabs')
        assert hasattr(self.rules, 'get_standard_deduction')
        assert hasattr(self.rules, 'get_rebate_87a')
        assert hasattr(self.rules, 'get_surcharge_rates')
        assert hasattr(self.rules, 'get_cess_rate')
        assert hasattr(self.rules, 'is_deduction_eligible')


class TestDeductionCatalog:
    """Test the deduction catalog functionality."""

    def setup_method(self):
        """Setup test instance."""
        self.catalog = DeductionCatalog()

    def test_all_deductions_present(self):
        """Test that all expected deductions are in catalog."""
        sections = self.catalog.get_all_sections()
        assert "80C" in sections
        assert "80D" in sections
        assert "80CCD(2)" in sections
        assert "24(b)" in sections
        assert "44ADA" in sections

    def test_deduction_info(self):
        """Test getting detailed deduction information."""
        info = self.catalog.get_deduction_info("80C")
        assert info is not None
        assert info.section == "80C"
        assert info.max_limit == 150000
        assert "OLD" in info.applicable_regimes
        assert "NEW" not in info.applicable_regimes

    def test_eligibility_old_regime(self):
        """Test eligibility checks for old regime."""
        assert self.catalog.is_eligible("80C", "OLD") is True
        assert self.catalog.is_eligible("80D", "OLD") is True
        assert self.catalog.is_eligible("80CCD(2)", "OLD") is True

    def test_eligibility_new_regime(self):
        """Test eligibility checks for new regime."""
        assert self.catalog.is_eligible("80C", "NEW") is False
        assert self.catalog.is_eligible("80D", "NEW") is False
        assert self.catalog.is_eligible("80CCD(2)", "NEW") is True
        assert self.catalog.is_eligible("44ADA", "NEW") is True

    def test_list_eligible_deductions(self):
        """Test listing eligible deductions by regime."""
        old_deductions = self.catalog.list_eligible_deductions("OLD")
        new_deductions = self.catalog.list_eligible_deductions("NEW")

        # Old regime should have more deductions
        assert len(old_deductions) > len(new_deductions)

        # Check specific deductions
        old_sections = [d.section for d in old_deductions]
        new_sections = [d.section for d in new_deductions]

        assert "80C" in old_sections
        assert "80C" not in new_sections
        assert "80CCD(2)" in old_sections
        assert "80CCD(2)" in new_sections

    def test_nonexistent_deduction(self):
        """Test handling of non-existent deduction section."""
        info = self.catalog.get_deduction_info("999")
        assert info is None
        assert self.catalog.is_eligible("999", "OLD") is False


class TestSlabBoundaryConditions:
    """Test slab boundary conditions across all AYs."""

    def test_ay_2025_26_slab_transitions(self):
        """Test slab transition points for AY 2025-26."""
        rules = AY2025_26RuleSet()

        # Old regime transitions
        old_slabs = rules.get_slabs(TaxRegime.OLD)
        assert old_slabs[0].upper_limit == 250000
        assert old_slabs[1].lower_limit == 250000
        assert old_slabs[1].upper_limit == 500000
        assert old_slabs[2].lower_limit == 500000

        # New regime transitions
        new_slabs = rules.get_slabs(TaxRegime.NEW)
        assert new_slabs[0].upper_limit == 300000
        assert new_slabs[1].lower_limit == 300000
        assert new_slabs[1].upper_limit == 700000

    def test_ay_2026_27_slab_transitions(self):
        """Test slab transition points for AY 2026-27."""
        rules = AY2026_27RuleSet()

        # Should maintain same boundaries as AY 2025-26
        old_slabs = rules.get_slabs(TaxRegime.OLD)
        new_slabs = rules.get_slabs(TaxRegime.NEW)

        assert old_slabs[0].upper_limit == 250000
        assert new_slabs[0].upper_limit == 300000


class TestRebateBoundaryConditions:
    """Test rebate boundary conditions."""

    def test_ay_2025_26_rebate_boundaries(self):
        """Test rebate eligibility boundaries for AY 2025-26."""
        rules = AY2025_26RuleSet()

        old_rebate = rules.get_rebate_87a(TaxRegime.OLD)
        assert old_rebate.max_taxable_income == 500000
        assert old_rebate.max_rebate_amount == 12500

        new_rebate = rules.get_rebate_87a(TaxRegime.NEW)
        assert new_rebate.max_taxable_income == 700000
        assert new_rebate.max_rebate_amount == 25000

    def test_ay_2026_27_rebate_boundaries(self):
        """Test rebate eligibility boundaries for AY 2026-27."""
        rules = AY2026_27RuleSet()

        # Should maintain same limits as AY 2025-26
        old_rebate = rules.get_rebate_87a(TaxRegime.OLD)
        new_rebate = rules.get_rebate_87a(TaxRegime.NEW)

        assert old_rebate.max_taxable_income == 500000
        assert new_rebate.max_taxable_income == 700000


class TestStandardDeductionComparison:
    """Test standard deduction changes across AYs."""

    def test_ay_2025_26_standard_deduction(self):
        """Test standard deduction for AY 2025-26."""
        rules = AY2025_26RuleSet()
        sd = rules.get_standard_deduction(TaxRegime.OLD)
        assert sd.amount == 50000

    def test_ay_2026_27_standard_deduction_increase(self):
        """Test standard deduction increase for AY 2026-27."""
        rules = AY2026_27RuleSet()
        sd = rules.get_standard_deduction(TaxRegime.OLD)
        assert sd.amount == 75000

    def test_standard_deduction_comparison(self):
        """Test that standard deduction increased from AY 2025-26 to 2026-27."""
        rules_25_26 = AY2025_26RuleSet()
        rules_26_27 = AY2026_27RuleSet()

        sd_25_26 = rules_25_26.get_standard_deduction(TaxRegime.OLD)
        sd_26_27 = rules_26_27.get_standard_deduction(TaxRegime.OLD)

        assert sd_26_27.amount > sd_25_26.amount
        assert sd_26_27.amount - sd_25_26.amount == 25000

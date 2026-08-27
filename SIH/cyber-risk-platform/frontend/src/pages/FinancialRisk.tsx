import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Alert,
  Chip,
  LinearProgress,
  Button
} from '@mui/material';
import { Refresh as RefreshIcon } from '@mui/icons-material';
import { OrganizationFinancialRiskSummary } from '../types/financialRisk';
import financialRiskService from '../services/financialRiskService';
import { useAuth } from '../context/AuthContext';

const formatCurrency = (value: number, currency: string = 'INR') => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: currency,
    maximumFractionDigits: 0,
  }).format(value);
};

const FinancialRisk: React.FC = () => {
  const { user } = useAuth();
  const [summary, setSummary] = useState<OrganizationFinancialRiskSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchFinancialRisk = async () => {
    if (!user?.organization_id) return;
    setLoading(true);
    try {
      const data = await financialRiskService.getOrganizationFinancialRisk(user.organization_id);
      setSummary(data);
      setError(null);
    } catch (err: any) {
      if (err.response?.status === 404) {
        setSummary(null);
      } else {
        setError('Failed to load financial risk data.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRecalculate = async () => {
    if (!user?.organization_id) return;
    setLoading(true);
    try {
      await financialRiskService.calculateOrganizationFinancialRisk(user.organization_id);
      await fetchFinancialRisk();
    } catch (err) {
      setError('Failed to recalculate financial risk.');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFinancialRisk();
  }, [user?.organization_id]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!summary) {
    return (
      <Box p={3}>
        <Typography variant="h4" gutterBottom fontWeight="bold">Financial Risk Quantification</Typography>
        <Alert severity="info" action={<Button color="inherit" size="small" onClick={handleRecalculate}>Recalculate Now</Button>}>
          No financial risk data found for your organization. You may need to run the Risk Engine first or explicitly configure financial assumptions.
        </Alert>
      </Box>
    );
  }

  const { aggregate_breakdown } = summary;

  // Prepare data for the breakdown bars
  const breakdownItems = [
    { label: 'Data Loss', value: aggregate_breakdown.data_loss, color: '#f44336' },
    { label: 'Business Interruption', value: aggregate_breakdown.business_interruption_loss, color: '#ff9800' },
    { label: 'Regulatory/Legal', value: aggregate_breakdown.regulatory_legal_exposure, color: '#9c27b0' },
    { label: 'Recovery', value: aggregate_breakdown.recovery_loss, color: '#2196f3' },
    { label: 'Direct Cost', value: aggregate_breakdown.direct_loss, color: '#00bcd4' },
    { label: 'Customer Impact', value: aggregate_breakdown.customer_impact, color: '#e91e63' },
    { label: 'Third-Party', value: aggregate_breakdown.third_party_impact, color: '#795548' },
    { label: 'Fraud', value: aggregate_breakdown.fraud_loss, color: '#607d8b' },
    { label: 'Reputation', value: aggregate_breakdown.reputation_revenue_impact, color: '#4caf50' },
  ].filter(item => item.value > 0).sort((a, b) => b.value - a.value);

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4" fontWeight="bold">
          Financial Risk Quantification
        </Typography>
        <Button 
          variant="outlined" 
          startIcon={<RefreshIcon />}
          onClick={handleRecalculate}
        >
          Recalculate
        </Button>
      </Box>

      {/* Overview Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={4}>
          <Card elevation={0} sx={{ border: '1px solid #e0e0e0', bgcolor: '#fff3e0' }}>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Modeled Potential Loss
              </Typography>
              <Typography variant="h4" color="warning.main" fontWeight="bold">
                {formatCurrency(summary.total_potential_loss, summary.currency)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Total exposure across all identified risk scenarios.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card elevation={0} sx={{ border: '1px solid #e0e0e0', bgcolor: '#ffebee' }}>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Expected Annual Loss (EAL)
              </Typography>
              <Typography variant="h4" color="error.main" fontWeight="bold">
                {formatCurrency(summary.total_expected_annual_loss, summary.currency)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Probability-weighted annualized financial exposure.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card elevation={0} sx={{ border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Financial Model Confidence
              </Typography>
              <Box display="flex" alignItems="center" gap={2} mt={1}>
                <Typography variant="h4" fontWeight="bold">
                  {summary.average_confidence.toFixed(0)}%
                </Typography>
                <Chip 
                  label={summary.average_confidence >= 80 ? 'High' : summary.average_confidence >= 50 ? 'Medium' : 'Low'}
                  color={summary.average_confidence >= 80 ? 'success' : summary.average_confidence >= 50 ? 'warning' : 'error'}
                  size="small"
                />
              </Box>
              <Typography variant="caption" color="text.secondary">
                Based on completeness of data and assumptions.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Breakdown Visualization */}
      <Card elevation={0} sx={{ border: '1px solid #e0e0e0', mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom fontWeight="bold">Potential Loss Breakdown</Typography>
          <Box mt={3}>
            {breakdownItems.map((item, idx) => {
              const percentage = (item.value / summary.total_potential_loss) * 100;
              return (
                <Box key={idx} mb={2}>
                  <Box display="flex" justifyContent="space-between" mb={0.5}>
                    <Typography variant="body2">{item.label}</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {formatCurrency(item.value, summary.currency)} ({percentage.toFixed(1)}%)
                    </Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={percentage} 
                    sx={{ 
                      height: 8, 
                      borderRadius: 4, 
                      bgcolor: '#f5f5f5',
                      '& .MuiLinearProgress-bar': { bgcolor: item.color }
                    }} 
                  />
                </Box>
              );
            })}
          </Box>
        </CardContent>
      </Card>

      {/* Top Assets Table */}
      <Typography variant="h6" gutterBottom fontWeight="bold" mt={4}>
        Top Financial Risk Assets
      </Typography>
      <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid #e0e0e0' }}>
        <Table>
          <TableHead sx={{ bgcolor: '#f5f5f5' }}>
            <TableRow>
              <TableCell><strong>Asset ID</strong></TableCell>
              <TableCell align="right"><strong>Cyber Risk Factor</strong></TableCell>
              <TableCell align="right"><strong>Event Frequency</strong></TableCell>
              <TableCell align="right"><strong>Potential Loss</strong></TableCell>
              <TableCell align="right"><strong>Expected Annual Loss</strong></TableCell>
              <TableCell align="right"><strong>Confidence</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {summary.top_financial_risk_assets.map((asset) => (
              <TableRow key={asset.id} hover>
                <TableCell>{asset.asset_id.substring(0, 8)}...</TableCell>
                <TableCell align="right">
                  <Chip 
                    label={asset.metadata?.factors?.likelihood || "N/A"} 
                    size="small" 
                    color="error" 
                    variant="outlined" 
                  />
                </TableCell>
                <TableCell align="right">{asset.metadata?.annual_event_frequency || 0} / yr</TableCell>
                <TableCell align="right" sx={{ color: 'warning.main', fontWeight: 'medium' }}>
                  {formatCurrency(asset.potential_loss, asset.currency)}
                </TableCell>
                <TableCell align="right" sx={{ color: 'error.main', fontWeight: 'bold' }}>
                  {formatCurrency(asset.expected_loss, asset.currency)}
                </TableCell>
                <TableCell align="right">{asset.confidence}%</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

    </Box>
  );
};

export default FinancialRisk;

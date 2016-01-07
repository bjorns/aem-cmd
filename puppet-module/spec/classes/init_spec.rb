require 'spec_helper'
describe 'acmd' do

  context 'with defaults for all parameters' do
    it { should contain_class('acmd') }
  end
end
